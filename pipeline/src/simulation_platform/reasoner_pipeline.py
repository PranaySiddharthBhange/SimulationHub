"""The active pipeline: `reasoner.Reasoner` + `sources.Packet` +
`contracts.py`/free text directly -- the user's explicit architectural
choice for this fork (a structured, multi-call-per-stage predecessor
pipeline existed earlier and has since been removed).

    Stage 1: read documents ONE AT A TIME (page-sized CHUNKS of a single
             document, if even one document overflows a call's safe
             context budget) -> write one free-text "understanding" file
             per document/chunk immediately as it's produced (see
             `skills/stage1_understanding.py`). Real bug this avoids:
             a single whole-project call needed 17023 tokens just for the
             tank dataset; per-document/per-chunk calls stay small enough
             to never need more than the shared default context window.
    Merge: read ALL of Stage 1's per-document understanding files -> write one
           resolved `Understanding` JSON brief.
    Clarify: pause for human answers to unresolved Merge questions and persist
             those decisions separately from the original brief.
    Stage 2: read the merged understanding plus confirmed Clarify answers ->
             write the SysML v2 file directly (`contracts.SysMLDraft.code`),
             one call, no separate planning/mapping/validation calls.
    Stage 3: read the merged understanding, confirmed answers, and concise SysML flow -> write an
             ordered multi-file Modelica bundle using verified Standard
             Library components (`contracts.ModelicaDraft.files`).

Stage 1 is the only stage that reads the raw documents. Local Ollama mode
uses gemma3:4b for text extraction and explicitly skips image-only files.
OpenAI mode can process the original visual evidence when that is required.
Stages 2/3 work from the extracted understanding and never read raw images.
"""

from __future__ import annotations

import csv
import json
import re
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from simulation_platform.config import PlatformSettings
from simulation_platform.contracts import (
    CANONICAL_STATUS,
    Check, Clarification, MergeClarification, MermaidDraft, ModelicaDraft, Simulation, SysMLDraft, Understanding, ValidationReport,
)
from simulation_platform.project_store import ProjectStore
from simulation_platform.reasoner import Reasoner
from simulation_platform.prompts.merge_notes import MERGE_PROMPT
from simulation_platform.prompts.flow_diagram import FLOW_DIAGRAM
from simulation_platform.skills.domains import domain_skill_block
from simulation_platform.skills.modelica_catalog import modelica_catalog_block
from simulation_platform.skills.stage1_understanding import SYSTEM_PROMPT as DOCUMENT_UNDERSTANDING_PROMPT
from simulation_platform.skills.stage2_sysml import SYSML
from simulation_platform.skills.stage3_modelica import MODELICA
from simulation_platform.skills.stage4_validation import VALIDATION
from simulation_platform.sources import Packet, Source, read_source
from simulation_platform.utils.run_log import RunLog
from simulation_platform.workspace import Workspace

# ~2000 tokens of raw text -- comfortably inside the shared per-call context
# budget alongside the system prompt and response, even for the largest
# single chunk. See module docstring for the real bug this exists to avoid.
_MAX_CHARS_PER_CHUNK = 6000

# A cloud extraction has no reason to be split at the local model's budget.
# Measured across the three benchmark datasets, a whole project is 19k-31k
# tokens and the largest single document is well under that, so every document
# fits in one call. Splitting them was actively harmful: an engineering
# register carries a value and the note that supersedes it thousands of
# characters apart, and no 6000-char chunk ever saw both, which made the
# supersession reasoning structurally impossible at Stage 1. The ceiling here
# exists only so a pathological file still gets split rather than rejected.
_CLOUD_MAX_CHARS_PER_CHUNK = 400_000

# A table this long is a recorded trajectory, not a scenario input. Sending it
# verbatim wastes most of the call and invites the model to treat a reference
# output as a forcing function, which `prompts/common.py` explicitly forbids.
_TABLE_SAMPLE_ROWS = 15
_TABLE_MAX_EVENT_ROWS = 40
_TABLE_DISCRETE_MAX_DISTINCT = 25
_MAX_QUOTE_REPAIRS = 1


@contextmanager
def _traced_stage(name: str, run_log: RunLog | None = None):
    """Prints a live, timestamped marker on entry/exit (for a terminal
    watching in real time) AND, if `run_log` is given, durably records the
    same start/end -- with the real elapsed time and, if it raised, the
    real exception -- as JSONL in the project folder (see `RunLog`)."""

    started = time.monotonic()
    print(f"\n=== [{datetime.now().strftime('%H:%M:%S')}] {name} ===", flush=True)
    if run_log is not None:
        with run_log.stage(name):
            yield
    else:
        yield
    elapsed = time.monotonic() - started
    print(f"--- [{datetime.now().strftime('%H:%M:%S')}] {name} done in {elapsed:.1f}s ---", flush=True)


@dataclass
class StageResult:
    stage: str
    project_id: str
    status: str
    details: dict


def _workspace(projects_root: Path | None = None) -> Workspace:
    return Workspace(projects_root or PlatformSettings.load().projects_root)


def _understanding_dir(ws: Workspace, project_id: str) -> Path:
    return ws.extracted_dir(project_id) / "understanding"


def _sysml_generated_path(ws: Workspace, project_id: str) -> Path:
    return ws.sysml_dir(project_id) / "generated" / f"{project_id}.sysml"


def _modelica_generated_dir(ws: Workspace, project_id: str) -> Path:
    return ws.modelica_dir(project_id) / "generated"


def _modelica_manifest_path(ws: Workspace, project_id: str) -> Path:
    """Manifest for the current ordered multi-file Modelica bundle."""

    return _modelica_generated_dir(ws, project_id) / "modelica_manifest.json"


def _draft_files(draft: ModelicaDraft) -> dict[str, str]:
    """Preserve the LLM's dependency order when passing files to omc."""

    return {file.filename: file.code for file in draft.files}


def _render_modelica_bundle(draft: ModelicaDraft) -> str:
    return "\n\n".join(f"--- {file.filename} ({file.role}) ---\n{file.code}" for file in draft.files)


def _archive_modelica_attempt(ws: Workspace, project_id: str, attempt: int, draft: ModelicaDraft) -> Path:
    """Preserve every Stage 3 draft, including failed compiler attempts."""
    attempt_dir = _modelica_generated_dir(ws, project_id) / "attempts" / f"attempt_{attempt:03d}"
    attempt_dir.mkdir(parents=True, exist_ok=True)
    for file in draft.files:
        (attempt_dir / file.filename).write_text(file.code, encoding="utf-8")
    (attempt_dir / "attempt_manifest.json").write_text(
        json.dumps({
            "attempt": attempt,
            "entry_class": draft.entry_class,
            "files": [file.model_dump(exclude={"code"}) for file in draft.files],
            "library_components": draft.library_components,
            "corrections": draft.corrections,
            "references": [reference.model_dump() for reference in draft.references],
        }, indent=2) + "\n",
        encoding="utf-8",
    )
    return attempt_dir
# Every reserved word in the Modelica Language Specification. Using one as an
# identifier is the single most expensive Stage 3 failure mode found live: a
# generated valve component declared `RealOutput flow;` (`flow` is reserved for
# connector flow variables), and omc reported it as
# `No viable alternative near token: RealOutput` -- pointing at the token BEFORE
# the offending one. Three consecutive repair attempts rewrote the innocent
# `RealOutput` declaration and never touched `flow`, so the loop could not
# converge. Naming it here turns an undiagnosable parser error into one precise
# instruction, without spending an omc run to get it.
_MODELICA_RESERVED_WORDS = frozenset("""
algorithm and annotation block break class connect connector constant
constrainedby der discrete each else elseif elsewhen encapsulated end
enumeration equation expandable extends external false final flow for function
if import impure in initial inner input loop model not operator or outer output
package parameter partial protected public pure record redeclare replaceable
return stream then true type when while within
""".split())

# `time` is not reserved, but it is the built-in independent variable -- a
# component that declares its own `time` shadows it and produces a model whose
# equations silently mean something else.
_MODELICA_BUILTIN_NAMES = frozenset({"time"})


def _icon_graphics(code: str) -> str | None:
    """The body of a class's `Icon(...)` annotation, or None if it has none.

    Returned by balanced-paren scan rather than a regex, because an icon's
    graphics list nests parentheses several levels deep and a non-greedy match
    stops at the first inner `)`.
    """

    start = code.find("Icon(")
    if start < 0:
        return None
    depth, index = 0, start + len("Icon")
    while index < len(code):
        if code[index] == "(":
            depth += 1
        elif code[index] == ")":
            depth -= 1
            if depth == 0:
                return code[start:index + 1]
        index += 1
    return code[start:]


# A `Text` element alone renders as a labelled blank box -- the shape is what
# makes a component recognisable at a glance. Confirmed live across runs: the
# same prompt produced a proper two-triangle valve symbol on one attempt and a
# bare text label on the next, so icon quality has to be checked, not asked for.
_ICON_SHAPES = ("Rectangle(", "Polygon(", "Ellipse(", "Line(", "Bitmap(")


def _equation_section(code: str) -> str:
    """Only the equation/algorithm bodies of a class.

    A component declaration's parameter modifiers (`Ctrl c(limit=limit)`) read
    exactly like equations to a line parser, which made the loop detector report
    `limit -> limit` self-loops that do not exist.
    """

    parts = re.split(r"(?m)^\s*(?:initial\s+)?(?:equation|algorithm)\b", code)
    return "\n".join(parts[1:]) if len(parts) > 1 else ""


def _algebraic_feedthrough(code: str, members: list[str]) -> set[tuple[str, str]]:
    """Which of a class's outputs depend on its inputs with no state in between.

    A dependency that passes through `der(x)` (a continuous state) or through a
    variable assigned inside a `when` (a discrete state) is NOT feedthrough --
    that is what makes a feedback control loop solvable. Only the algebraic
    paths can close an unsolvable loop, so only those are reported.
    """

    body = re.sub(r"(?s)\bwhen\b.*?\bend\s+when\s*;", " ", _equation_section(code))  # discrete state
    depends: dict[str, set[str]] = {}
    for line in body.splitlines():
        line = line.split("//")[0].strip().rstrip(";")
        if "=" not in line or line.startswith(("connect", "parameter", "constant")):
            continue
        lhs, _, rhs = line.partition("=")
        lhs, rhs = lhs.strip(), rhs.strip()
        if lhs.startswith("der(") or not re.fullmatch(r"[A-Za-z_]\w*", lhs):
            continue  # a state's derivative gives no algebraic dependency
        depends.setdefault(lhs, set()).update(re.findall(r"\b([A-Za-z_]\w*)\b", rhs))

    def reaches(start: str) -> set[str]:
        seen, stack, found = set(), [start], set()
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            if node in members:
                found.add(node)
            stack.extend(depends.get(node, ()))
        return found

    return {(source, name) for name in members for source in reaches(name) if source != name}


def _algebraic_loops(draft: ModelicaDraft, system_code: str) -> list[list[str]]:
    """Find signal loops in the system model that contain no state.

    Built over symbols, not components, because the same loop appears equally
    often routed through ordinary equations and intermediate variables as
    through `connect()` -- three consecutive live runs closed a vessel/valve
    loop, one via connects and two via equations, and every one of them
    compiled, simulated and reported success with the whole loop solved as a
    constant zero.
    """

    ports = _connector_members(draft)
    feedthrough = {
        name: _algebraic_feedthrough(other.code, ports.get(name, []))
        for other in draft.files if other.role != "system"
        for name in re.findall(r"(?m)^\s*(?:partial\s+)?(?:model|block)\s+(\w+)", other.code)
    }

    edges: dict[str, set[str]] = {}
    def link(source: str, target: str) -> None:
        edges.setdefault(source, set()).add(target)

    # Inside each instance: an output that algebraically feeds through from an input.
    for class_name, pairs in feedthrough.items():
        for instance in re.findall(rf"(?m)^\s*{re.escape(class_name)}\s+([A-Za-z_]\w*)", system_code):
            for source, target in pairs:
                link(f"{instance}.{source}", f"{instance}.{target}")

    body = re.sub(r"(?s)\bwhen\b.*?\bend\s+when\s*;", " ", _equation_section(system_code))
    for line in body.splitlines():
        line = line.split("//")[0].strip().rstrip(";")
        connect = re.fullmatch(r"connect\s*\(\s*([\w.]+)\s*,\s*([\w.]+)\s*\)(?:\s*annotation.*)?", line)
        if connect:
            link(connect.group(1), connect.group(2))
            continue
        if "=" not in line or line.startswith(("parameter", "constant", "connect")):
            continue
        lhs, _, rhs = line.partition("=")
        lhs, rhs = lhs.strip(), rhs.split("annotation")[0].strip()
        if not re.fullmatch(r"[A-Za-z_][\w.]*", lhs) or lhs.startswith("der("):
            continue
        for symbol in re.findall(r"\b([A-Za-z_][\w.]*)\b", rhs):
            if symbol != lhs:
                link(symbol, lhs)

    # Any cycle in this graph is algebraic by construction: every state-crossing
    # dependency was excluded when the edges were built.
    found: list[list[str]] = []
    colour: dict[str, int] = {}
    def walk(node: str, path: list[str]) -> None:
        colour[node] = 1
        for nxt in sorted(edges.get(node, ())):
            if colour.get(nxt) == 1:
                cycle = path[path.index(nxt):] + [nxt] if nxt in path else [nxt, node, nxt]
                if len(found) < 3:
                    found.append(cycle)
            elif colour.get(nxt, 0) == 0:
                walk(nxt, path + [nxt])
        colour[node] = 2

    for node in sorted(edges):
        if colour.get(node, 0) == 0:
            walk(node, [node])
    return found


def _instance_count(draft: ModelicaDraft, class_code: str) -> int:
    """How many times the class defined in `class_code` is placed by the system."""

    names = re.findall(r"(?m)^\s*(?:partial\s+)?(?:model|block)\s+(\w+)", class_code)
    system = next((f.code for f in draft.files if f.role == "system"), "")
    return sum(
        len(re.findall(rf"(?m)^\s*{re.escape(name)}\s+[A-Za-z_]\w*", system))
        for name in names
    )


def _connector_members(draft: ModelicaDraft) -> dict[str, list[str]]:
    """Map each class this bundle defines to the connector members it declares."""

    # INPUTS only. An unconnected input is the real hazard: Modelica silently
    # defaults it to zero, so the model compiles, simulates and reports success
    # while that signal path carries nothing. Found live, twice: a vessel's
    # `requestedOutflow` input was never driven, so every transfer flow in the
    # process was zero for the whole run and only the trajectory revealed it.
    #
    # An unread OUTPUT cannot do that, and demanding a consumer for every one
    # asks for instruments the brief does not have. The NaCl plant has level
    # instruments on four of its seven vessels, so the outputs reporting the
    # other three genuinely have no reader; that check failed six attempts
    # across two runs without the compiler ever being reached. A component
    # nothing connects AT ALL is still caught, by the floating-component check
    # below.
    # A CONDITIONAL connector -- `RealInput Qcmd if use_heater;` -- does not
    # exist on an instance whose guard is false, so there is nothing there to
    # wire and demanding it is a false positive. This matters because the
    # prompt also asks for ONE reusable class instantiated per unit, and a
    # reusable vessel class carries the union of every role's ports: only the
    # evaporator has a heater command, only some vessels report composition.
    # Without this exemption those two rules cannot both be satisfied, and the
    # NaCl case failed every attempt on it without ever reaching the compiler.
    # An UNguarded connector must still be wired, which is the real check.
    members: dict[str, list[str]] = {}
    declaration = re.compile(
        r"(?m)^\s*Modelica\.[\w.]*Interfaces\.\w*Input\s+([A-Za-z_]\w*)(?![^;\n]*\bif\b)"
    )
    for file in draft.files:
        if file.role == "system":
            continue
        for match in re.finditer(r"(?m)^\s*(?:partial\s+)?(?:model|block)\s+(\w+)", file.code):
            names = declaration.findall(file.code)
            if names:
                members[match.group(1)] = names
    return members


def _diagram_issues(draft: ModelicaDraft) -> list[str]:
    """The bundle is inspected in OMEdit, so an undrawable diagram is a defect.

    Found live: a bundle that compiled and simulated perfectly rendered as two
    blank rectangles, because the whole plant had been collapsed into one
    aggregate class and not one `connect()` carried a `Line` annotation. None of
    that is visible to the compiler, so nothing rejected it.
    """

    issues: list[str] = []
    # Every library connector, not just the causal Blocks signals: magnetic
    # ports, heat ports, mechanical flanges, electrical pins and fluid ports all
    # need placing and connecting too, and a bundle in one of those domains was
    # otherwise invisible to these checks.
    connector = re.compile(r"Modelica\.[\w.]*Interfaces\.\w+\b")
    for file in draft.files:
        if file.role == "system":
            plain = [
                number for number, text in enumerate(file.code.splitlines(), 1)
                if re.match(r"\s*connect\s*\(", text) and "Line(" not in text
            ]
            if plain:
                shown = ", ".join(str(n) for n in plain[:8])
                issues.append(
                    f"- {file.filename}: {len(plain)} connect() statement(s) (line(s) {shown}) have no "
                    "graphical annotation. Every connection in the system diagram must carry "
                    "annotation(Line(points={{x1,y1},{x2,y2}}, color={...})) or the diagram cannot be "
                    "drawn and the bundle is not inspectable in OMEdit."
                )
            # A component that is placed but never connected renders as an icon
            # floating on its own, which is exactly what makes a generated
            # diagram look wrong to an engineer reading it.
            connected = set(re.findall(r"connect\s*\(\s*([A-Za-z_]\w*)[.,]", file.code))
            connected |= set(re.findall(r"connect\s*\([^,]+,\s*([A-Za-z_]\w*)[.)]", file.code))
            placed = re.findall(
                r"(?m)^\s*(?:[A-Za-z_]\w*\.)*[A-Za-z_]\w*\s+([A-Za-z_]\w*)\s*(?:\([^;]*\))?\s*annotation\s*\(\s*Placement",
                file.code,
            )
            # A component coupled through EQUATIONS rather than connectors is
            # not floating -- it is a different modelling style, and rejecting
            # it is a false positive that cannot be repaired away. Seen live: a
            # plant written with signal equations (`q = if cmd then ... B1.level
            # ...`) had three vessels reported as floating on every attempt, so
            # all five repairs were spent on a non-defect and the compiler never
            # ran once. Only a component nothing references at all is dead.
            body = "\n".join(
                line for line in file.code.splitlines() if not re.match(r"\s*connect\s*\(", line)
            )
            referenced = set(re.findall(r"\b([A-Za-z_]\w*)\s*\.", body))
            floating = [name for name in placed if name not in connected and name not in referenced]
            if floating:
                issues.append(
                    f"- {file.filename}: component(s) {', '.join(floating)} are placed in the diagram but "
                    "never appear in any connect() and are never referenced in an equation. Every component "
                    "shown must take part in the system -- a boundary source or sink is connected to the "
                    "first/last element of the material path, not left floating. Either wire it, use it, or "
                    "remove it."
                )

            # Component-level wiring is not enough: an actuator whose OUTPUT port
            # is left dangling still looks connected (its command input is wired)
            # while the material path silently routes around it. Found live: a
            # supply source was connected straight to the vessel it feeds, so the
            # inlet valve gated nothing and the vessel filled whatever the valve
            # was commanded to do.
            # A pair of components wired BOTH ways with nothing in between is an
            # algebraic loop, not a feedback control loop (that one runs through
            # the controller, so it is three or more components long). Found live:
            # a vessel's actual outflow drove the downstream valve's requested
            # flow while that valve's actual flow drove the vessel's outflow
            # demand. The system compiled, simulated and reported success with
            # every flow in the loop solved as a constant zero, so no transfer
            # ever happened and nothing in the toolchain objected.
            loops = _algebraic_loops(draft, file.code)
            if loops:
                shown = "; ".join(" -> ".join(loop) for loop in loops)
                issues.append(
                    f"- {file.filename}: algebraic signal loop(s) with no state anywhere in them: {shown}. "
                    "The solver can satisfy such a loop with every signal in it stuck at zero, so the "
                    "process silently transports nothing while the run still reports success -- this is not "
                    "a compiler error and only the trajectory reveals it. Break it by making the chain "
                    "one-directional: an on/off actuator on a fixed-flow brief produces its OWN nominal "
                    "flow from its command alone (`flowOut = if openCmd then qNominal else 0`) and needs no "
                    "upstream flow input at all; the vessel upstream subtracts that same flow and limits it "
                    "to its own inventory inside its own equations, and the vessel downstream adds it. "
                    "Never feed a vessel's resulting outflow back into the actuator that sets it."
                )

            ports = _connector_members(draft)
            dangling: list[str] = []
            for class_name, members in ports.items():
                for instance in re.findall(rf"(?m)^\s*{re.escape(class_name)}\s+([A-Za-z_]\w*)", file.code):
                    # Referenced ANYWHERE in the system model counts, not only in a
                    # connect(): reading an output in an ordinary equation (for a
                    # reported variable, say) is a legitimate use. What this must
                    # catch is a port that nothing in the system touches at all.
                    dangling += [
                        f"{instance}.{member}" for member in members
                        if not re.search(rf"\b{re.escape(instance)}\.{re.escape(member)}\b", file.code)
                    ]
            if dangling:
                issues.append(
                    f"- {file.filename}: connector(s) {', '.join(sorted(dangling))} are declared on placed "
                    "components but nothing in the system model uses them. The material path must run "
                    "THROUGH every element the brief puts in it -- source into the first actuator, each "
                    "actuator into the unit it feeds -- never around one of them. Fix each port by "
                    "connecting it into the path, or by reading it in an equation if it is genuinely a "
                    "terminal report, or by removing it from the component."
                )

            # Library instances count as much as this bundle's own classes: a
            # diagram assembled from Standard Library vessels and valves is the
            # better outcome, not a worse one, because each of those already
            # carries its own icon and connectors.
            if len(placed) < 4:
                issues.append(
                    f"- {file.filename}: the system diagram places only {len(placed)} component(s) "
                    f"({', '.join(placed) or 'none'}), counting library and generated classes alike. "
                    "The diagram must show each physical unit the brief names separately -- every vessel, "
                    "every valve, every named source or sink, plus the controller -- as its own instance. "
                    "Do not aggregate the plant into a single combined class."
                )
        else:
            icon = _icon_graphics(file.code)
            if icon is None:
                issues.append(
                    f"- {file.filename}: this class has no Icon annotation, so it renders as a blank box. "
                    "Give it an Icon(graphics={...}) that depicts what it is, including "
                    'Text(extent={{-100,100},{100,140}}, textString="%name").'
                )
            elif not any(shape in icon for shape in _ICON_SHAPES):
                issues.append(
                    f"- {file.filename}: this class's Icon contains no shape, only text, so it renders as a "
                    "labelled blank box. Draw what the component actually is using Rectangle, Polygon, "
                    "Ellipse or Line: a vessel as a body rectangle plus a partial fill rectangle, an on/off "
                    "valve as two opposed triangles meeting at a point, a boundary source or sink as an "
                    "ellipse, a controller as a block with its port names."
                )
            elif '"%name"' not in icon and _instance_count(draft, file.code) > 1:
                # Only worth failing over when the class really has several
                # instances -- a one-off component reads fine with a static
                # label, and rejecting an otherwise correct bundle for this
                # costs a whole repair attempt.
                issues.append(
                    f"- {file.filename}: this class's Icon never draws %name, and the system places several "
                    'instances of it, so they all show the same label. Add '
                    'Text(extent={{-100,100},{100,140}}, textString="%name").'
                )
        for number, text in _declaration_lines(file.code):
            if connector.search(text) and "Placement(" not in text:
                issues.append(
                    f"- {file.filename}:{number}: this connector declaration has no Placement annotation, "
                    "so connections to it cannot be positioned. Put inputs on the left edge and outputs on "
                    "the right edge of the -100..100 icon coordinate system."
                )
    return issues


def _declaration_lines(code: str) -> list[tuple[int, str]]:
    """The lines of each class that declare things, excluding its equation and
    algorithm bodies.

    Needed because a Boolean expression in a body reads exactly like a
    declaration to a line regex: `startPulse and (pre(mode) == Mode.IDLE)`
    scans as type `startPulse`, name `and`, open paren -- which made the
    reserved-word check reject a perfectly valid controller.
    """

    header = re.compile(r"^(?:partial\s+|encapsulated\s+)*"
                        r"(?:model|block|connector|record|class|package|function|type)\b")
    out: list[tuple[int, str]] = []
    declaring = False
    for number, raw in enumerate(code.splitlines(), 1):
        stripped = raw.strip()
        if header.match(stripped):
            declaring = True
            continue
        if re.match(r"^(?:initial\s+)?(?:equation|algorithm)\b", stripped):
            declaring = False
            continue
        if re.match(r"^(?:public|protected)\b", stripped):
            declaring = True
            continue
        if declaring and stripped:
            out.append((number, raw))
    return out


def _when_block_issues(filename: str, code: str) -> list[str]:
    """Two `when` mistakes OpenModelica reports in a way the model can't act on.

    Both were observed live on the tank dataset in consecutive attempts:
    an equation-section `when` holding an `if/elseif` chain with no `else`
    (illegal -- every branch of an if-equation inside a when-equation must
    assign the same left-hand sides), and `reinit` sharing a when-branch with
    ordinary assignments, which omc rejects as a locationless
    `Internal error BackendDAECreate.lowerWhenEqn: equation not handled`.
    """

    issues: list[str] = []
    in_algorithm = False
    when_start: int | None = None
    when_lines: list[str] = []

    for number, raw in enumerate(code.splitlines(), 1):
        stripped = raw.strip()
        if when_start is None:
            if re.match(r"^(algorithm|initial\s+algorithm)\b", stripped):
                in_algorithm = True
            elif re.match(r"^(equation|initial\s+equation)\b", stripped):
                in_algorithm = False
            elif re.match(r"^(public|protected)\b", stripped):
                in_algorithm = False
            if re.match(r"^when\b", stripped):
                when_start, when_lines = number, [stripped]
            continue

        when_lines.append(stripped)
        if not re.match(r"^end\s+when\s*;", stripped):
            continue

        body = "\n".join(when_lines)
        if not in_algorithm and re.search(r"(?m)^\s*if\b", body) and not re.search(r"(?m)^\s*else\b", body):
            issues.append(
                f"- {filename}:{when_start}: this `when` is in an EQUATION section and its if/elseif chain "
                "has no `else` branch. Every branch of an if-equation inside a when-equation must assign "
                "exactly the same set of variables, so a missing `else` is an error. Move the whole mode "
                "dispatcher into an `algorithm` section and assign with `:=`, where an if/elseif chain may "
                "legally omit the `else` and unassigned variables keep their previous value."
            )
        if "reinit(" in body and re.search(r"(?m)^\s*[A-Za-z_][\w.]*\s*:?=", body):
            issues.append(
                f"- {filename}:{when_start}: this `when` mixes `reinit(...)` with ordinary assignments in "
                "the same branch, which OpenModelica rejects as an internal `lowerWhenEqn` error with no "
                "usable location. Remove the `reinit` entirely: represent elapsed time as a plain equation "
                "`waitElapsed = time - tEnter;` over a `discrete Real tEnter` that the transition sets, "
                "instead of resetting a continuous timer state."
            )
        when_start, when_lines = None, []

    return issues


def _modelica_static_issues(draft: ModelicaDraft, checked_variables: set[str] | None = None) -> list[str]:
    """Catch deterministic Modelica mistakes before spending an omc run.

    Each check here exists because the real compiler's own message for that
    mistake is either wrong about where the problem is (reserved-word
    identifiers) or does not name the construct at all -- in both cases the
    repair loop provably could not converge on the real error text alone.
    """

    declaration = re.compile(
        r"(?m)^\s*(?:(?:parameter|constant|discrete|input|output|final|inner|outer|flow|stream)\s+)*"
        r"(?:Real|Boolean|Integer)\s+([^;]+);"
    )
    # Any component declaration: a (possibly dotted) type name followed by the
    # instance name. Deliberately broad -- it only feeds the reserved-word check.
    component = re.compile(
        r"(?m)^\s*(?:(?:parameter|constant|discrete|input|output|final|inner|outer|replaceable)\s+)*"
        r"(?P<type>[A-Za-z_]\w*(?:\.\w+)*)\s+(?P<name>[A-Za-z_]\w*)\s*(?:\(|;|\[|=|\bannotation\b)"
    )
    connection = re.compile(
        r"\bconnect\s*\(\s*([^,()]+?)\s*,\s*([^,()]+?)\s*\)", re.MULTILINE,
    )
    empty_array = re.compile(r"=\s*\{\s*\}")
    issues: list[str] = []

    def line_of(code: str, offset: int) -> int:
        return code.count("\n", 0, offset) + 1

    for file in draft.files:
        plain_scalars: set[str] = set()
        for match in declaration.finditer(file.code):
            for item in match.group(1).split(","):
                name_match = re.match(r"\s*([A-Za-z_]\w*)", item)
                if name_match:
                    plain_scalars.add(name_match.group(1))

        for number, text in _declaration_lines(file.code):
            match = component.match(text)
            if match is None:
                continue
            name = match.group("name")
            if match.group("type") in _MODELICA_RESERVED_WORDS:
                continue  # `parameter Real x` style prefixes, already handled above
            if name in _MODELICA_RESERVED_WORDS:
                issues.append(
                    f"- {file.filename}:{number}: '{name}' is a RESERVED "
                    f"Modelica keyword and cannot be used as an identifier. Rename this declaration (for "
                    f"example '{name}Signal' or a descriptive physical name) and update every reference to "
                    f"it, including any '<instance>.{name}' member access in other files. Note the compiler "
                    f"reports this as a parse error on the PRECEDING token, so do not trust its location."
                )
            elif name in _MODELICA_BUILTIN_NAMES:
                issues.append(
                    f"- {file.filename}:{number}: '{name}' is the built-in "
                    f"Modelica variable and must not be redeclared. Rename it."
                )

        issues.extend(_when_block_issues(file.filename, file.code))

        for match in empty_array.finditer(file.code):
            issues.append(
                f"- {file.filename}:{line_of(file.code, match.start())}: empty array constructor '{{}}' is "
                "not valid Modelica. Omit the attribute entirely (for example write "
                "'annotation(Icon())' or drop the graphics attribute) instead of giving it an empty list."
            )

        for match in connection.finditer(file.code):
            for endpoint in (match.group(1).strip(), match.group(2).strip()):
                bare = re.fullmatch(r"([A-Za-z_]\w*)(?:\[[^\]]+\])?", endpoint)
                if bare and bare.group(1) in plain_scalars:
                    issues.append(
                        f"- {file.filename}:{line_of(file.code, match.start())}: connect() endpoint "
                        f"'{endpoint}' is an ordinary scalar, not a connector. Replace the connection with "
                        "an equation assignment or use a proper Modelica connector."
                    )

    issues.extend(_diagram_issues(draft))
    issues.extend(_frozen_state_issues(draft, checked_variables or set()))
    return issues


def _inert_variables(
    result_summary: dict[str, dict[str, float]], checked_variables: set[str]
) -> list[str]:
    """Checked quantities that never move across the whole simulated run.

    A command that is deliberately never issued is not evidence of a dead
    model -- the brief may not exercise it -- so only quantities that CHANGE
    as the process runs are judged: levels, compositions, temperatures. A
    genuinely constant one among those means the process did not happen.

    Requires the summary to carry at least a few of them, so a model whose
    result file names its variables differently degrades to no finding rather
    than to a false accusation.
    """

    continuous = [
        name for name in checked_variables
        if any(token in name.lower() for token in ("level", "_w_", "w_nacl", "temp", "_t", "conc", "mass", "flow"))
        and not name.lower().endswith("_cmd")
    ]
    observed = {name: result_summary[name] for name in continuous if name in result_summary}
    if len(observed) < 2:
        return []
    return sorted(
        name for name, stats in observed.items()
        if stats.get("min") is not None and stats.get("min") == stats.get("max")
    )


def _checked_variable_names(understanding: Understanding) -> set[str]:
    """Identifiers appearing in the brief's acceptance-check expressions."""

    names: set[str] = set()
    for check in understanding.checks:
        names.update(re.findall(r"[A-Za-z_]\w*", check.expression))
    # Operators and numeric helpers that the tokeniser also picks up.
    return names - {"and", "or", "not", "abs", "max", "min", "sqrt", "der", "time", "if", "then", "else"}


def _frozen_state_issues(draft: ModelicaDraft, checked_variables: set[str]) -> list[str]:
    """A quantity the acceptance checks read must be computed, not asserted.

    The worst outcome this pipeline can produce is not a model that fails to
    compile; it is one that compiles, simulates to completion and reports
    numbers that were typed in. Found live on the evaporation plant: the bundle
    contained no `der()` anywhere and pinned eleven reported quantities to
    literals, including `B6_temp_C = 20.0` and `B7_temp_C = 25.0` -- which are
    exactly the values their two acceptance checks compare against. Those two
    checks passed. Every structural check passed, the compiler passed, and the
    result file was constants.

    Only variables the checks actually read are examined. A genuine constant
    elsewhere -- an ambient pressure, a fixed setpoint -- is normal modelling.
    """

    if not checked_variables:
        return []
    issues: list[str] = []
    literal = re.compile(r"(?m)^\s*([A-Za-z_]\w*)\s*=\s*[-+]?[0-9][0-9_.eE+-]*\s*;")
    for file in draft.files:
        equations = _equation_section(file.code)
        frozen = sorted({
            name for name in literal.findall(equations) if name in checked_variables
        })
        if frozen:
            issues.append(
                f"- {file.filename}: {', '.join(frozen)} are read by the acceptance checks but are "
                "assigned a literal constant, so the simulation reports a number that was typed in "
                "rather than computed. Every quantity a check reads must follow from the model: a "
                "state from its own `der(...)` balance, a composition from the species balance, a "
                "measurement from the component it measures. If the value genuinely cannot be "
                "derived from the brief, say so in `corrections` -- never stand a literal in for it."
            )
    return issues


# Presentation defects. Real, worth telling the model about, and NOT worth one
# of three repair attempts: a class with no icon still simulates correctly, and
# a helper source left unwired is a loose end rather than a wrong model.
#
# They were costing more than they were worth. Across two NaCl runs an icon
# complaint and an unwired tie-off constant took the first two attempts of
# each, leaving one attempt for the real problem. A rewrite forced by a
# cosmetic rejection also takes the simplest path available, and on the run
# where that happened the model abandoned a Modelica.Fluid network it had
# already built and finished with a hand-written one.
_ADVISORY_MARKERS = (
    "has no Icon annotation",
    "has no Placement annotation",
    "are placed in the diagram but never appear in any connect() and are never referenced",
)


def _split_blocking(issues: list[str]) -> tuple[list[str], list[str]]:
    """Separate issues that make the model WRONG from ones that make it untidy."""

    advisory = [i for i in issues if any(marker in i for marker in _ADVISORY_MARKERS)]
    blocking = [i for i in issues if i not in advisory]
    return blocking, advisory


def _force_split(piece: str) -> list[str]:
    """Guarantees no returned piece exceeds `_MAX_CHARS_PER_CHUNK`, no
    matter what separators (or lack of them) the source text uses -- line-
    based first (keeps a spreadsheet's one-row-per-line structure intact
    when possible), falling back to raw character slicing only if even a
    single line is still too big on its own."""

    if len(piece) <= _MAX_CHARS_PER_CHUNK:
        return [piece]

    lines = [line for line in piece.split("\n") if line.strip()]
    if len(lines) > 1:
        result: list[str] = []
        current = ""
        for line in lines:
            if len(line) > _MAX_CHARS_PER_CHUNK:
                if current:
                    result.append(current)
                    current = ""
                result.extend(line[i:i + _MAX_CHARS_PER_CHUNK] for i in range(0, len(line), _MAX_CHARS_PER_CHUNK))
            elif current and len(current) + len(line) > _MAX_CHARS_PER_CHUNK:
                result.append(current)
                current = line
            else:
                current += ("\n" if current else "") + line
        if current:
            result.append(current)
        return result

    return [piece[i:i + _MAX_CHARS_PER_CHUNK] for i in range(0, len(piece), _MAX_CHARS_PER_CHUNK)]


def _chunk_source_text(text: str) -> list[str]:
    """Page-based chunks when the source has `[page N]` markers (PDFs,
    see `sources.py::read_source`), else paragraph-based -- packed
    greedily up to `_MAX_CHARS_PER_CHUNK` so a small document still costs
    just ONE call, and only a genuinely large one gets split."""

    page_starts = [m.start() for m in re.finditer(r"\n\[page \d+\]", text)]
    if page_starts:
        boundaries = [0, *page_starts, len(text)]
        pieces = [text[boundaries[i]:boundaries[i + 1]] for i in range(len(boundaries) - 1)]
    else:
        pieces = text.split("\n\n")
    pieces = [p for p in pieces if p.strip()] or [text]

    # One-line-per-record data (CSV/TSV rows, and anything else with no
    # blank-line structure) has no `\n\n` breaks at all -- `split("\n\n")`
    # above returns the WHOLE text as a single "piece" (confirmed live on a
    # 981-row spreadsheet). If that one piece still has to be force-split by
    # line to fit the chunk budget, every chunk after the first loses line 1
    # -- for a CSV, that's the column header -- leaving nothing but bare
    # numbers. Confirmed live: faced with a chunk of pure numeric CSV rows
    # and no header, the model invented fictitious generic entities
    # ("Sensor1".."Sensor20") and a fabricated topology between them to
    # explain numbers it had no real name for. Re-attach the real first line
    # to every later chunk so it never has to guess what the data in front
    # of it actually is.
    header = pieces[0].split("\n", 1)[0] if len(pieces) == 1 and "\n" in pieces[0] else None

    # Real bug found live: a 981-row spreadsheet's extracted text has no
    # `\n\n` breaks at all (one line per row) -- `split("\n\n")` returned
    # the WHOLE 19817-char dump as a single "piece", silently defeating
    # chunking entirely (the packing loop below only ever splits BETWEEN
    # pieces, never breaks one that's already oversized on its own). Any
    # piece still bigger than the budget on its own now gets force-split
    # by line, and any single LINE still too big gets force-split by raw
    # character count -- there is always a hard ceiling on chunk size,
    # regardless of what separator (or lack of one) the source text uses.
    pieces = [p for original in pieces for p in _force_split(original)]

    chunks: list[str] = []
    current = ""
    for piece in pieces:
        if current and len(current) + len(piece) > _MAX_CHARS_PER_CHUNK:
            chunks.append(current)
            current = piece
        else:
            current += ("\n\n" if current else "") + piece
    if current:
        chunks.append(current)

    if header is not None and len(chunks) > 1:
        chunks = [chunks[0]] + [f"{header}\n{c}" for c in chunks[1:]]
    return chunks


# Pure-image files (per `sources.py::read_source`) carry ALL their real
# content in `.images` -- their `.text` is just a fixed placeholder
# ("Image evidence is attached..."). Real user decision: skip vision
# entirely for now (found live: a vision call on a 2-image document took
# 320s, vs. seconds for text-only calls) -- a pure-image file has nothing
# useful to extract without it, so it's skipped outright rather than
# wasting a call on the placeholder text.
_IMAGE_ONLY_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}


def _sendable_text(source: Source) -> str:
    """The document text one Stage 1 call should actually see.

    A parsed CSV/TSV arrives with `table` populated. Those files in this
    benchmark are recorded run trajectories of hundreds of rows, and the useful
    evidence in them is the column schema, the range each quantity covers, and
    WHEN things changed -- not the numbers themselves.

    Sampling the first N rows, which is what this did first, is the worst
    possible slice of a trajectory: confirmed live on a 901-row, 900-second run
    whose first command lands at t=20, the head sample was fifteen identical
    all-zero rows from the dead time before anything happened. It showed no
    event at all and read as though the command schedule were empty. Rows are
    now chosen where a discrete column actually CHANGES, which puts the real
    event structure in the same space.
    """

    if source.table is None or len(source.table) <= _TABLE_SAMPLE_ROWS:
        return source.text

    rows = source.table
    columns = list(rows[0])

    def numbers(column: str) -> list[float]:
        values = []
        for row in rows:
            try:
                values.append(float(row[column]))
            except (TypeError, ValueError):
                return []
        return values

    # Step-like columns (few distinct values) carry the events; a column with a
    # different value in every row is a continuously varying signal.
    discrete = [
        c for c in columns
        if 1 < len({row.get(c) for row in rows}) <= _TABLE_DISCRETE_MAX_DISTINCT
    ]

    summary = []
    for column in columns:
        values = numbers(column)
        if values:
            summary.append(f"  {column}: {min(values):g} .. {max(values):g}")
        else:
            seen = {str(row.get(column)) for row in rows}
            if len(seen) <= _TABLE_DISCRETE_MAX_DISTINCT:
                summary.append(f"  {column}: {', '.join(sorted(seen))}")

    if discrete:
        cardinality = {c: len({row.get(c) for row in rows}) for c in discrete}
        # Score each change by the most selective column that moved: a mode or a
        # valve command has very few distinct values, a countdown timer has many.
        # Thinning purely by position dropped a stage transition because timer
        # decrements crowded it out, so rank by significance and keep the top
        # ones rather than every n-th.
        events: list[tuple[int, int]] = [(0, 0)]
        previous = tuple(rows[0].get(c) for c in discrete)
        for index, row in enumerate(rows[1:], 1):
            current = tuple(row.get(c) for c in discrete)
            if current != previous:
                moved = [c for c, before, after in zip(discrete, previous, current) if before != after]
                events.append((index, min(cardinality[c] for c in moved)))
                previous = current
        if events[-1][0] != len(rows) - 1:
            events.append((len(rows) - 1, 0))
        if len(events) > _TABLE_MAX_EVENT_ROWS:
            events = sorted(events, key=lambda e: (e[1], e[0]))[:_TABLE_MAX_EVENT_ROWS]
        picked = sorted(index for index, _ in events)
        heading = (
            f"rows where a discrete column changes value, which is the event structure of this run "
            f"({len(picked)} of {len(rows)} rows shown; the rest repeat the previous row's state):"
        )
    else:
        step = max(1, len(rows) // _TABLE_SAMPLE_ROWS)
        picked = list(range(0, len(rows), step))[:_TABLE_SAMPLE_ROWS]
        heading = (
            f"no column changes in steps, so {len(picked)} evenly spaced rows of {len(rows)} are "
            "shown as a sample:"
        )

    sample = "\n".join(
        "  " + " | ".join(f"{c}={rows[i].get(c, '')}" for c in columns) for i in picked
    )
    return (
        f"[tabular data: {len(rows)} rows, {len(columns)} columns]\n"
        f"columns: {', '.join(columns)}\n"
        "These are RECORDED values -- an observation of a run that already happened, not a "
        "scenario input and not a command schedule.\n"
        f"range of each column across all {len(rows)} rows:\n" + "\n".join(summary) + "\n"
        f"{heading}\n{sample}"
    )


def _normalise(text: str) -> str:
    """Whitespace-insensitive form used only for quote matching."""

    return re.sub(r"\s+", " ", text).strip().lower()


def _verify_quotes(extracted, source_text: str) -> list[str]:
    """Every quote must really occur in the document. Returns the ones that don't.

    This is the whole point of asking for quotes: it turns "did the model make
    this up?" from a judgement call into a substring test. Confirmed necessary --
    an earlier free-text Stage 1 invented component tags and a requirement that
    appear nowhere in the source documents, and nothing detected it until the
    fabricated entities surfaced three stages later.
    """

    haystack = _normalise(source_text)
    bad: list[str] = []
    values = [(entity, value) for entity in extracted.entities for value in entity.values]
    for entity, value in values:
        if entity.from_image:
            continue
        quote = (value.quote or "").strip()
        if not quote or _normalise(quote) not in haystack:
            bad.append(
                f"{entity.name}/{value.quantity!r} = {value.value!r}: "
                + ("no quote given" if not quote else f"quote not found -- {quote[:100]!r}")
            )
    for item in [*extracted.entities, *extracted.relationships, *extracted.facts]:
        if item.from_image:
            continue  # a diagram has no substring to match
        quote = (item.quote or "").strip()
        label = getattr(item, "name", None) or getattr(item, "statement", None) or getattr(item, "subject", "?")
        if not quote:
            bad.append(f"{label!r}: no quote given")
        elif _normalise(quote) not in haystack:
            bad.append(f"{label!r}: quote not found in the document -- {quote[:120]!r}")
    return bad


_STATUS_SYNONYMS = {
    "released": "approved", "issued": "approved", "final": "approved",
    "effective": "current", "active": "current", "in_force": "current",
    "latest": "current", "applicable": "current",
    "stale": "superseded", "obsolete": "superseded", "replaced": "superseded",
    "deprecated": "superseded", "legacy": "archived", "historical": "archived",
    "draft": "proposed", "candidate": "proposed", "recommended": "proposed",
    "typical": "nominal", "rated": "nominal", "design": "nominal",
    "as-built": "as_built", "asbuilt": "as_built", "commissioned": "as_built",
    "recorded": "measured", "test": "measured", "reported": "observed",
}


def _canonical_status(status: str) -> str:
    """Map a document's own status wording onto a canonical value.

    The field is free text on purpose (a strict enum failed a whole extraction
    on `released`), so normalisation happens here instead: the raw word stays in
    the sidecar, and this gives the comparable form.
    """

    raw = (status or "").strip().lower().replace(" ", "_")
    if raw in CANONICAL_STATUS:
        return raw
    return _STATUS_SYNONYMS.get(raw, _STATUS_SYNONYMS.get(raw.replace("_", "-"), raw or "unknown"))


def _tag(item) -> str:
    """Trailing provenance: the document's own id for an item and its page/sheet."""

    bits = [b for b in (getattr(item, "ref", ""), getattr(item, "anchor", "")) if b]
    return f"  <{' '.join(bits)}>" if bits else ""


def _render_extraction(extracted) -> str:
    """Render a typed extraction into the same eight-section note format.

    Merge reads these notes as text, so the structure stays an internal quality
    mechanism rather than a new handoff format: the cloud path gains schema
    validation and quote checking without changing anything downstream.
    """

    category_heading = {
        "requirement": "Requirements",
        "constraint": "Constraints",
        "behavior": "Behaviors",
        "physical_relationship": "Physical relationships",
        "control_law": "Control laws",
        "scheduled_command": "Scheduled commands",
    }
    lines = [f"Subject: {extracted.subject}", f"Document kind: {extracted.kind}", ""]

    if extracted.entities:
        lines.append("## Entities")
        for entity in extracted.entities:
            parts = [f"* {entity.name} -- {entity.kind}{_tag(entity)}"]
            if entity.aliases:
                parts.append(f"aliases: {', '.join(entity.aliases)}")
            lines.append("; ".join(parts))
            for value in entity.values:
                unit = f" {value.unit}" if value.unit else ""
                canonical = _canonical_status(value.status)
                shown = canonical if canonical == value.status.strip().lower() else f"{canonical}/{value.status}"
                status = "" if canonical == "unknown" else f" [{shown}]"
                replaces = f" (supersedes/superseded: {value.supersedes})" if value.supersedes else ""
                lines.append(f"    - {value.quantity}: {value.value}{unit}{status}{replaces}")
        lines.append("")

    if extracted.relationships:
        lines.append("## Relationships")
        for rel in extracted.relationships:
            detail = f" ({rel.detail})" if rel.detail else ""
            lines.append(f"* {rel.subject} {rel.predicate} {rel.object}{detail}{_tag(rel)}")
        lines.append("")

    for category, heading in category_heading.items():
        items = [f for f in extracted.facts if f.category == category]
        if not items:
            continue
        lines.append(f"## {heading}")
        lines.extend(
            f"* {item.statement}{'' if _canonical_status(item.status) == 'unknown' else f' [{_canonical_status(item.status)}]'}{_tag(item)}"
            for item in items
        )
        lines.append("")

    if extracted.unreadable:
        lines.append("## Unreadable")
        lines.extend(f"* {item}" for item in extracted.unreadable)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _extract_structured(reasoner, packet, chunk_text: str, rel: str, out_path: Path, run_log: RunLog | None) -> str:
    """One cloud extraction: typed result, quotes verified against the source.

    The structure is an internal quality mechanism -- the note written to disk
    is still the eight-section text Merge already reads. The typed result is
    kept beside it as `.extraction.json` so a reviewer can see exactly which
    span of the document every recorded fact came from.
    """

    from simulation_platform.contracts import ExtractedDocument
    from simulation_platform.skills.stage1_understanding import CLOUD_EXTRACTION_PROMPT

    context = ""
    extracted = None
    for attempt in range(_MAX_QUOTE_REPAIRS + 1):
        try:
            extracted = reasoner.ask(CLOUD_EXTRACTION_PROMPT, context, ExtractedDocument, packet)
        except Exception as exc:
            # A schema rejection must not end a run that may be extracting
            # dozens of documents. Found live: the model returned a status word
            # the schema did not list, and the whole document was lost. Hand the
            # validation error back once rather than failing the stage.
            if extracted is not None or attempt == _MAX_QUOTE_REPAIRS:
                raise
            print(f"    [Stage 1] {rel}: response rejected, retrying once -- {type(exc).__name__}", flush=True)
            if run_log is not None:
                run_log.event("extraction_invalid_response", stage=1, document=rel, detail=str(exc)[:1500])
            context = (
                "Your previous answer could not be accepted:\n\n"
                f"{str(exc)[:2000]}\n\n"
                "Return the extraction again, correcting exactly what the message reports "
                "and changing nothing else."
            )
            continue
        unverified = _verify_quotes(extracted, chunk_text)
        if not unverified:
            break
        print(f"    [Stage 1] {rel}: {len(unverified)} unverifiable quote(s)", flush=True)
        if run_log is not None:
            run_log.event(
                "extraction_quotes_unverified", stage=1, document=rel,
                attempt=attempt + 1, count=len(unverified), items=unverified[:20],
            )
        if attempt == _MAX_QUOTE_REPAIRS:
            # Keep the items rather than dropping them silently; they are marked
            # in the note so Merge can weigh them, and the sidecar records which.
            break
        context = (
            "Your previous answer contained items whose `quote` is not an exact "
            "substring of the document you were given:\n\n"
            + "\n".join(f"- {item}" for item in unverified)
            + "\n\nRe-read the document and return the extraction again. For each item "
            "above, either copy the real supporting text verbatim as its quote, or "
            "remove the item entirely because the document does not support it. Do "
            "not reword the document to make a quote match."
        )

    unverified = _verify_quotes(extracted, chunk_text)
    out_path.with_suffix(".extraction.json").write_text(
        json.dumps(
            {**extracted.model_dump(), "unverified_quotes": unverified},
            indent=2, ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )
    note = _render_extraction(extracted)
    if unverified:
        note += (
            "\n## Unverified\n"
            "The following items could not be matched to text in this document and "
            "may be unreliable:\n"
            + "\n".join(f"* {item}" for item in unverified) + "\n"
        )
    return note


def _understand_documents(ws: Workspace, project_id: str, run_log: RunLog | None = None, stage1_backend: str | None = None) -> list[Path]:
    """Understand documents with a selectable Stage 1 backend.

    "ollama" uses the configured local gemma text model and skips image-only
    files. "openai" uses the configured OpenAI model (normally gpt-5.4) and
    can process the original visual evidence. Raw parsing remains deterministic
    and every generated note is written incrementally.
    """

    settings = PlatformSettings.load()
    backend = (stage1_backend or settings.stage1_backend).strip().lower()
    if backend not in {"ollama", "openai"}:
        raise ValueError("Stage 1 backend must be ollama or openai")
    reasoner = Reasoner(
        settings,
        1,
        backend="openai" if backend == "openai" else "ollama",
        model_override=settings.openai_model if backend == "openai" else None,
        run_log=run_log,
    )

    documents_dir = ws.documents_dir(project_id)
    understanding_dir = _understanding_dir(ws, project_id)
    understanding_dir.mkdir(parents=True, exist_ok=True)
    doc_paths = sorted(p for p in documents_dir.rglob("*") if p.is_file())
    written: list[Path] = []

    for doc_index, doc_path in enumerate(doc_paths, 1):
        rel = doc_path.relative_to(documents_dir).as_posix()
        is_image_only = doc_path.suffix.lower() in _IMAGE_ONLY_EXTENSIONS
        if is_image_only and backend == "ollama":
            print(
                f"    [Stage 1:{backend}] document {doc_index}/{len(doc_paths)}: {rel} "
                "-- skipped (local Gemma mode is text-only)",
                flush=True,
            )
            continue
        try:
            source = read_source(doc_path, rel)
        except Exception as exc:
            print(f"    [Stage 1] skipping {rel}: {exc}", flush=True)
            continue

        budget = _CLOUD_MAX_CHARS_PER_CHUNK if backend == "openai" else _MAX_CHARS_PER_CHUNK
        body = _sendable_text(source)
        chunks = _chunk_source_text(body) if len(body) > budget else [body]
        for chunk_index, chunk_text in enumerate(chunks):
            # Images ride with the first chunk. They used to be dropped for every
            # document that was not a pure image file, which silently discarded
            # four page/embedded images per benchmark dataset -- diagram pages of
            # a URS, a datasheet and a test procedure among them -- even though
            # the parser had already extracted them.
            chunk_source = Source(rel, chunk_text, images=source.images if chunk_index == 0 else [])
            packet = Packet([chunk_source])
            label = f"{rel}" + (f" (chunk {chunk_index + 1}/{len(chunks)})" if len(chunks) > 1 else "")
            attached = f", {len(chunk_source.images)} image(s)" if chunk_source.images else ""
            print(f"    [Stage 1:{backend}] document {doc_index}/{len(doc_paths)}: {label}{attached}", flush=True)

            suffix = f"_chunk{chunk_index:02d}" if len(chunks) > 1 else ""
            out_path = understanding_dir / f"{doc_index:02d}_{doc_path.stem}{suffix}.txt"

            if backend == "openai":
                text = _extract_structured(
                    reasoner, packet, chunk_text, rel, out_path, run_log,
                )
            else:
                text = reasoner.ask_free_text(DOCUMENT_UNDERSTANDING_PROMPT, "", packet)

            out_path.write_text(text, encoding="utf-8")
            written.append(out_path)

    return written

def _load_all_understanding(ws: Workspace, project_id: str) -> str:
    files = sorted(_understanding_dir(ws, project_id).glob("*.txt"))
    return "\n\n".join(f"--- {p.name} ---\n{p.read_text(encoding='utf-8')}" for p in files)


def _merged_understanding_path(ws: Workspace, project_id: str) -> Path:
    return ws.extracted_dir(project_id) / "merged_understanding.json"


def _merged_narrative_path(ws: Workspace, project_id: str) -> Path:
    return ws.extracted_dir(project_id) / "merged_understanding.md"


def _render_understanding_markdown(understanding: Understanding) -> str:
    """The merged brief as a document a person can actually read.

    The narrative alone used to be written out as plain text, which left the
    parts a reviewer most needs to check -- the acceptance criteria, what was
    resolved against what evidence, what is still open -- visible only inside
    the JSON. They are the reviewable substance of this stage, so they belong
    in the readable artifact next to the prose.
    """

    simulation = understanding.simulation
    out: list[str] = [
        f"# {understanding.title}",
        "",
        "## Simulation",
        "",
        "| setting | value |",
        "| --- | --- |",
        f"| start time | {simulation.start_time} s |",
        f"| stop time | {simulation.stop_time} s |",
        f"| output samples | {simulation.intervals} |",
        f"| solver tolerance | {simulation.tolerance} |",
        "",
    ]
    if understanding.domains:
        out += ["**Domains:** " + ", ".join(f"`{d}`" for d in understanding.domains), ""]

    out += ["## Engineering brief", "", understanding.narrative.strip(), ""]

    if understanding.checks:
        out += [
            f"## Acceptance checks ({len(understanding.checks)})",
            "",
            "| # | when | expression | expected | tolerance | source |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for number, check in enumerate(understanding.checks, 1):
            when = check.kind if check.at_time is None else f"at {check.at_time:g} s"
            expression = check.expression.replace("|", "\\|")
            out.append(
                f"| {number} | {when} | `{expression}` | {check.expected:g} | "
                f"{check.absolute_tolerance:g} | {check.source} |"
            )
        out.append("")

    if understanding.resolutions:
        out += [f"## Conflicts resolved ({len(understanding.resolutions)})", ""]
        for item in understanding.resolutions:
            out += [f"### {item.topic}", "", f"**Adopted:** {item.chosen}", ""]
            if item.rejected:
                out += ["**Not adopted:**", ""] + [f"- {r}" for r in item.rejected] + [""]
            out += [f"**Evidence:** {item.reasoning}", ""]

    if understanding.questions:
        out += [f"## Open questions ({len(understanding.questions)})", ""]
        out += [f"{i}. {q}" for i, q in enumerate(understanding.questions, 1)] + [""]

    if understanding.assumptions:
        out += [f"## Assumptions ({len(understanding.assumptions)})", ""]
        out += [f"- {a}" for a in understanding.assumptions] + [""]

    if understanding.tables:
        out += ["## Source tables", "", "| document | role | why |", "| --- | --- | --- |"]
        out += [f"| {t.path} | `{t.role}` | {t.reason} |" for t in understanding.tables] + [""]

    return "\n".join(out).rstrip() + "\n"


def _clarified_answers_path(ws: Workspace, project_id: str) -> Path:
    return ws.extracted_dir(project_id) / "clarified_answers.json"


def _flow_diagram_path(ws: Workspace, project_id: str) -> Path:
    return ws.extracted_dir(project_id) / "system_flow.mmd"


def _load_clarified_answers(ws: Workspace, project_id: str) -> dict[str, str]:
    path = _clarified_answers_path(ws, project_id)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    answers = payload.get("answers", {}) if isinstance(payload, dict) else {}
    return {str(key): str(value) for key, value in answers.items() if str(value).strip()}


def _answers_record(
    clarifications: list[Clarification], answers: dict[str, str], *, from_file: bool = False,
) -> dict:
    """What was asked, what was answered, and where the answer came from.

    The distinction matters for review: an engineer accepting a resolution and
    an engineer overturning one look identical in a plain id-to-value map.

    `from_file` says the answers were already on disk rather than given this
    run, which keeps the record honest about who decided. Re-running Merge can
    reword a resolution it still reaches the same way, and comparing a stored
    answer against the new wording then reports a change nobody made -- seen
    live, where two carried-over answers that meant exactly what Merge now
    suggested were both recorded as human overrides.
    """

    decisions = []
    for item in clarifications:
        given = (answers.get(item.id) or "").strip()
        suggested = (item.suggested_value or "").strip()
        if not given:
            outcome = "unanswered"
        elif not suggested:
            outcome = "answered"
        elif given == suggested:
            outcome = "confirmed"
        else:
            outcome = "carried_over" if from_file else "changed_by_human"
        decisions.append({
            "id": item.id,
            "question": item.question,
            "merge_suggested": item.suggested_value,
            "answer": given,
            "outcome": outcome,
        })
    return {
        "questions": [c.question for c in clarifications],
        "answers": answers,
        "decisions": decisions,
    }


def _merge_clarifications(understanding: Understanding) -> list[Clarification]:
    """Everything a person should sign off: what Merge could not settle, and what it did.

    A resolved conflict is still a decision. Merge used to surface only its open
    questions, so as extraction improved and it began settling conflicts from
    the evidence, a reviewer saw fewer and fewer of them -- three to zero on one
    benchmark in a single run -- while the decisions themselves stayed just as
    consequential. Each resolution is therefore presented already answered with
    Merge's choice as the default, so confirming is one click and overriding is
    possible, but neither happens silently.
    """

    if understanding.clarifications:
        open_items = [Clarification(**item.model_dump()) for item in understanding.clarifications]
    else:
        open_items = [
            Clarification(
                id=f"merge_question_{index}",
                question=question,
                reasoning="Merge marked this decision as unresolved. Choose the governing value or explain the approved resolution before SysML generation.",
                suggested_value="",
                options=[],
            )
            for index, question in enumerate(understanding.questions, 1)
        ]

    confirmations = [
        Clarification(
            id=item.id,
            question=f"{item.topic}: Merge resolved this to {item.chosen}. Confirm, or choose a different value.",
            reasoning=(
                f"{item.reasoning}"
                + (f" Not adopted: {'; '.join(item.rejected)}." if item.rejected else "")
                + " This was decided from the evidence rather than left open, so it is"
                " already answered -- change it only if you disagree with that reading."
            ),
            suggested_value=item.chosen,
            options=[item.chosen, *item.rejected],
            resolved=True,
        )
        for item in understanding.resolutions
    ]
    return open_items + confirmations


def _load_merged_understanding(ws: Workspace, project_id: str) -> Understanding:
    path = _merged_understanding_path(ws, project_id)
    if path.exists():
        return Understanding.model_validate_json(path.read_text(encoding="utf-8"))
    # Consolidation is optional -- Stage 2 can run straight off the raw
    # per-document notes if it was skipped, just without entity resolution.
    return Understanding(
        title="System", narrative=_load_all_understanding(ws, project_id), simulation=Simulation(stop_time=10.0),
        checks=[],
    )


def _render_check(c: Check) -> str:
    tol = f"absolute tolerance {c.absolute_tolerance}" if c.absolute_tolerance else f"relative tolerance {c.relative_tolerance:.3%}"
    when = f"at t={c.at_time}" if c.kind == "at" and c.at_time is not None else f"{c.kind} value"
    return f"- {c.name}: {c.expression} == {c.expected} ({tol}), {when} -- source: {c.source}"


def _understanding_context(understanding: Understanding, clarified_answers: dict[str, str] | None = None) -> str:
    """Merge already resolves `checks` (exact expression/expected value/
    tolerance/when-it-applies), `assumptions`, and `questions` into clean
    structured fields -- real, confirmed gap: Stage 2/3 used to see only
    `narrative`, silently dropping all three, and relied on Merge having
    ALSO restated the same facts in prose (fragile -- correct here only
    because it happened to). Render them explicitly so Stage 2/3 get the
    precise values Merge resolved, not a re-parse of prose."""

    parts = [f"Engineering brief (title: {understanding.title}):\n\n{understanding.narrative}"]
    if understanding.checks:
        parts.append(
            "Acceptance checks resolved by Merge -- use these exact expressions, expected values, tolerances, "
            "and timing verbatim rather than re-deriving them from the narrative:\n"
            + "\n".join(_render_check(c) for c in understanding.checks)
        )
    if understanding.assumptions:
        parts.append(
            "Assumptions Merge already made -- keep these, don't silently re-decide them differently:\n"
            + "\n".join(f"- {a}" for a in understanding.assumptions)
        )
    if understanding.questions:
        parts.append(
            "Open questions Merge flagged as unresolved (these must be answered by the Clarify stage before SysML generation):\n"
            + "\n".join(f"- {q}" for q in understanding.questions)
        )
    if clarified_answers:
        parts.append(
            "Human-confirmed answers from the Clarify stage -- these decisions are authoritative:\n"
            + "\n".join(f"- {key}: {value}" for key, value in clarified_answers.items())
        )
    return "\n\n".join(parts)


def execute_merge(project_id: str, projects_root: Path | None = None) -> StageResult:
    """OpenAI-backed (user's explicit choice). Reads every Stage 1
    understanding file (written independently, per document/chunk, by the
    local model -- so the same real component may appear under different
    names in different files) and produces ONE resolved, coherent system
    understanding: entities renamed consistently, one narrative, and what
    equations/conditions are actually needed."""

    ws = _workspace(projects_root)
    run_log = RunLog(ws.run_log_path(project_id))
    combined = _load_all_understanding(ws, project_id)
    context = (
        "Per-document understanding notes, written independently per document "
        f"(may use inconsistent names for the same real component):\n\n{combined}"
    )

    settings = PlatformSettings.load()
    with _traced_stage("Merge (OpenAI): resolve entities, build one coherent system understanding", run_log):
        understanding: Understanding = Reasoner(
            settings, 2, backend="openai", model_override=settings.merge_model, run_log=run_log,
        ).ask(MERGE_PROMPT, context, Understanding, Packet([]))

    _merged_understanding_path(ws, project_id).write_text(understanding.model_dump_json(indent=2), encoding="utf-8")
    _merged_narrative_path(ws, project_id).write_text(_render_understanding_markdown(understanding), encoding="utf-8")

    return StageResult(
        stage="merge", project_id=project_id, status="READY",
        details={
            "title": understanding.title,
            "narrative_chars": len(understanding.narrative),
            "checks": len(understanding.checks),
            "assumptions": len(understanding.assumptions),
            "questions": len(understanding.questions),
        },
    )


def execute_clarify(
    project_id: str,
    projects_root: Path | None = None,
    clarify: Callable[[list[Clarification]], dict[str, str]] | None = None,
) -> StageResult:
    """Pause for human answers to Merge's unresolved questions.

    This stage does not call an LLM. It records the human decisions separately
    from the original merged brief so the source interpretation remains
    auditable and downstream stages can consume the confirmed answers.
    """
    ws = _workspace(projects_root)
    understanding = _load_merged_understanding(ws, project_id)
    answers_path = _clarified_answers_path(ws, project_id)
    existing = _load_clarified_answers(ws, project_id)
    clarifications = _merge_clarifications(understanding)
    # Prior answers only count when they actually cover what is being asked NOW.
    # Re-running Merge can change the question set -- resolving something that
    # used to be open, or raising a new conflict -- and this used to short
    # circuit on the mere existence of an answers file. Found live: after a
    # re-merge, four new clarifications went unanswered while six answers from
    # the previous question set were kept, and `_understanding_context` passes
    # whatever is in that file to Stage 2 and Stage 3 as authoritative.
    stale = {key: value for key, value in existing.items() if key not in {c.id for c in clarifications}}
    if stale:
        print(f"    [Clarify] discarding {len(stale)} answer(s) from a previous question set: "
              f"{', '.join(sorted(stale))}", flush=True)
        existing = {key: value for key, value in existing.items() if key not in stale}
    covered = bool(existing) and all(c.id in existing for c in clarifications)
    if covered or not clarifications:
        # Always rewrite, not only when the file is absent: the recorded
        # question set has to match the clarifications actually in force, and
        # skipping the write left a discarded question sitting in the file as
        # though it had been answered for this run.
        answers_path.write_text(
            json.dumps(_answers_record(clarifications, existing, from_file=True), indent=2) + "\n",
            encoding="utf-8",
        )
        diagram = execute_flow_diagram(project_id, projects_root=projects_root)
        return StageResult(
            stage="clarify", project_id=project_id, status="READY",
            details={"questions": len(clarifications), "answered": len(existing), "skipped": not clarifications, "diagram": diagram.details},
        )
    if clarify is None:
        return StageResult(
            stage="clarify", project_id=project_id, status="NEEDS_INPUT",
            details={"questions": len(clarifications), "answered": 0},
        )
    answers = {key: value.strip() for key, value in clarify(clarifications).items() if value and value.strip()}
    missing = [c.id for c in clarifications if c.id not in answers]
    if missing:
        raise ValueError(f"Clarify requires an answer for every Merge question: {', '.join(missing)}")
    answers_path.write_text(
        json.dumps(_answers_record(clarifications, answers), indent=2) + "\n",
        encoding="utf-8",
    )
    diagram = execute_flow_diagram(project_id, projects_root=projects_root)
    return StageResult(
        stage="clarify", project_id=project_id, status="READY",
        details={"questions": len(clarifications), "answered": len(answers), "diagram": diagram.details},
    )


def execute_flow_diagram(project_id: str, projects_root: Path | None = None) -> StageResult:
    """Generate the clarified system flow as a Mermaid source artifact."""
    ws = _workspace(projects_root)
    run_log = RunLog(ws.run_log_path(project_id))
    settings = PlatformSettings.load()
    understanding = _load_merged_understanding(ws, project_id)
    context = _understanding_context(understanding, _load_clarified_answers(ws, project_id))
    with _traced_stage("Clarify (OpenAI): generate Mermaid system flow", run_log):
        draft: MermaidDraft = Reasoner(
            settings, 2, backend="openai", model_override=settings.merge_model, run_log=run_log,
        ).ask(FLOW_DIAGRAM, context, MermaidDraft, Packet([]))
    code = draft.code.strip()
    if code.startswith("```"):
        code = code.split("\n", 1)[1] if "\n" in code else code
        if code.endswith("```"):
            code = code[:-3].rstrip()
    if not code.startswith("flowchart TD"):
        raise ValueError("Mermaid flow must begin with 'flowchart TD'")
    if "```" in code:
        raise ValueError("Mermaid flow contains Markdown fences")
    _flow_diagram_path(ws, project_id).write_text(code + "\n", encoding="utf-8")
    return StageResult(
        stage="clarify", project_id=project_id, status="READY",
        details={"filename": _flow_diagram_path(ws, project_id).name, "characters": len(code), "corrections": draft.corrections},
    )


def execute_reasoner_stage_1(
    project_id: str,
    docs_dir: Path | None = None,
    problem_path: Path | None = None,
    projects_root: Path | None = None,
    stage1_backend: str | None = None,
) -> StageResult:
    ws = _workspace(projects_root)
    run_log = RunLog(ws.run_log_path(project_id))
    store = ProjectStore(ws.projects_root)

    if docs_dir is not None:
        store.create_project(project_id, project_id, docs_dir)
    ws.ensure_layout(project_id)

    with _traced_stage("Stage 1: read documents one at a time, write per-document understanding", run_log):
        written = _understand_documents(ws, project_id, run_log, stage1_backend=stage1_backend)

    return StageResult(
        stage="stage_1", project_id=project_id, status="READY",
        details={"documents_understood": len(written), "files": [str(p) for p in written]},
    )


def execute_reasoner_stage_2(
    project_id: str,
    projects_root: Path | None = None,
    clarify: Callable[[list[Clarification]], dict[str, str]] | None = None,
) -> StageResult:
    """OpenAI-backed (user's explicit choice). Writes the SysML v2 file
    directly from the CONSOLIDATED understanding (falls back to the raw
    per-document notes if consolidation wasn't run). Real repair loop: if
    the real SysML v2 parser (`tools/sysml_validator.py`, the same jupyter
    kernel this whole platform has used all along) finds a syntax error, the
    exact error is fed back to the model
    for another attempt -- up to `MAX_REPAIR_ATTEMPTS` -- matching the
    auto-repair discipline the structured pipeline already used, not a
    new invention.

    Human review can occur in the preceding Clarify stage for Merge's open
    questions. The first SysML draft may also surface a handful of additional
    `clarifications` (see `contracts.Clarification`) for decisions discovered
    only while writing the model. When `clarify` is given, the API pauses and
    waits for a person to answer those questions (or accept suggested defaults)
    before the real-parser repair loop begins. `clarify=None` remains useful
    for tests and non-interactive callers: the draft proceeds with its own
    suggested values for these Stage 2-only questions."""

    from simulation_platform.tools import RealParserUnavailable, validate_files_with_real_parser

    ws = _workspace(projects_root)
    run_log = RunLog(ws.run_log_path(project_id))
    settings = PlatformSettings.load()
    understanding = _load_merged_understanding(ws, project_id)
    context = _understanding_context(understanding, _load_clarified_answers(ws, project_id))
    sysml_prompt = SYSML + domain_skill_block(understanding.domains)

    reasoner = Reasoner(settings, 2, backend="openai", run_log=run_log)
    issues_summary = ""

    with _traced_stage("Stage 2: draft + identify open questions", run_log):
        draft: SysMLDraft = reasoner.ask(sysml_prompt, context, SysMLDraft, Packet([]))

    if draft.clarifications:
        run_log.event(
            "clarification_requested", stage=2,
            questions=[c.model_dump() for c in draft.clarifications],
        )
        if clarify is not None:
            answers = clarify(draft.clarifications)
            run_log.event("clarification_answered", stage=2, answers=answers)
            answered_text = "\n".join(
                f"- {c.question}\n  Human-confirmed answer: {answers.get(c.id, c.suggested_value)}"
                for c in draft.clarifications
            )
            context = (
                f"{context}\n\nA human engineer reviewed these open questions from your first draft and gave "
                f"the following confirmed answers -- use them exactly, they are authoritative and supersede "
                f"your own earlier guess:\n\n{answered_text}"
            )
            with _traced_stage("Stage 2: rewrite with human-confirmed answers", run_log):
                draft = reasoner.ask(sysml_prompt, context, SysMLDraft, Packet([]))
        else:
            print(
                f"    [Stage 2] {len(draft.clarifications)} open question(s) raised, no reviewer attached "
                "-- proceeding on the model's own suggested defaults", flush=True,
            )

    for attempt in range(settings.max_repair_attempts + 1):
        if attempt > 0:
            prompt_context = (
                f"{context}\n\nYour previous attempt:\n\n{draft.code}\n\n"
                f"The real SysML v2 parser found these errors:\n\n{issues_summary}\n\n"
                "Before patching: re-read the engineering brief above and work out WHY this error happened in "
                "terms of what element of the actual system it was trying to represent, not just the parser's "
                "error text in isolation. Fix the root cause, and never drop, weaken, or silently simplify away "
                "something the brief actually requires (a component, a requirement, an interlock, a resolved "
                "parameter value) just to make the error go away -- if a fix would remove something required, "
                "find a different fix instead. Keep unrelated, already-correct parts of the model unchanged.\n\n"
                "Do not treat this as patching only the one reported line. Read the ENTIRE previous attempt "
                "above and, using your own full knowledge of real SysML v2 syntax (not just the specific "
                "errors listed), check the whole file for every other place the same class of mistake could "
                "also be present. You have a limited number of attempts against the real parser, so aim to "
                "return a file that passes on THIS attempt, not one that trades today's reported error for a "
                "different one next attempt."
            )
            with _traced_stage(f"Stage 2: write SysML v2 (attempt {attempt + 1}/{settings.max_repair_attempts + 1})", run_log):
                draft = reasoner.ask(sysml_prompt, prompt_context, SysMLDraft, Packet([]))

        if not settings.use_real_sysml_parser:
            break
        try:
            issues = validate_files_with_real_parser(
                {"System.sysml": draft.code}, timeout=settings.sysml_parser_timeout_seconds,
            )
        except RealParserUnavailable as exc:
            print(f"    [Stage 2] real SysML parser unavailable, skipping validation: {exc}", flush=True)
            run_log.event("validation_attempt", stage=2, attempt=attempt + 1, tool="sysml_parser", status="UNAVAILABLE", detail=str(exc))
            break
        if not issues:
            print(f"    [Stage 2] real parser: PASSED ({attempt + 1} attempt(s))", flush=True)
            issues_summary = ""  # otherwise StageResult.remaining_issues would show a stale prior error
            run_log.event("validation_attempt", stage=2, attempt=attempt + 1, tool="sysml_parser", status="PASSED")
            break
        issues_summary = "\n".join(f"- {i.file}:{i.line}: {i.message}" for i in issues)
        print(f"    [Stage 2] real parser found {len(issues)} issue(s), attempt {attempt + 1}:\n{issues_summary}", flush=True)
        run_log.event(
            "validation_attempt", stage=2, attempt=attempt + 1, tool="sysml_parser", status="FAILED",
            issue_count=len(issues), issues=issues_summary,
        )

    path = _sysml_generated_path(ws, project_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(draft.code, encoding="utf-8")

    if issues_summary:
        raise RuntimeError(
            "Stage 2 exhausted its SysML parser repair attempts; the last draft was saved for inspection "
            f"but is not parser-valid:\n{issues_summary}"
        )

    return StageResult(
        stage="stage_2", project_id=project_id, status="READY",
        details={
            "file": str(path), "code_chars": len(draft.code), "corrections": draft.corrections,
            "remaining_issues": issues_summary or None,
            "clarifications": [c.model_dump() for c in draft.clarifications],
        },
    )


def execute_reasoner_stage_3(project_id: str, projects_root: Path | None = None) -> StageResult:
    """Write an ordered, graphical, Standard-Library-based Modelica bundle
    from the consolidated understanding + Stage 2's concise SysML flow.
    Real repair loop: if the real `omc` compiler (`tools/modelica_validator.py`,
    an actual `simulate()`, not just `checkModel()` -- see that module's own
    docstring for why) reports
    errors, they're fed back to the model for another attempt -- up to
    `MAX_REPAIR_ATTEMPTS`."""

    from simulation_platform.tools import CompilerUnavailable, compile_files

    ws = _workspace(projects_root)
    run_log = RunLog(ws.run_log_path(project_id))
    settings = PlatformSettings.load()
    understanding = _load_merged_understanding(ws, project_id)
    sysml_code = _sysml_generated_path(ws, project_id).read_text(encoding="utf-8")

    context = f"{_understanding_context(understanding, _load_clarified_answers(ws, project_id))}\n\nSysML v2 model (already generated):\n\n{sysml_code}"
    modelica_prompt = (
        MODELICA
        + domain_skill_block(understanding.domains)
        + modelica_catalog_block(understanding.domains)
    )
    reasoner = Reasoner(settings, 3, backend="openai", run_log=run_log)
    draft: ModelicaDraft | None = None
    errors_summary = ""
    # Only the immediately previous attempt used to be sent back, so the loop
    # had no memory: run live on the tank dataset it oscillated between a
    # discrete algebraic loop and a failed C build for five straight attempts,
    # each "fix" reintroducing the error from two attempts earlier. The full
    # rejection history makes a repeat visible to the model as a repeat.
    history: list[str] = []

    for attempt in range(settings.max_repair_attempts + 1):
        history_block = (
            "\n\nEvery earlier attempt in THIS run and why it was rejected. Do not reintroduce a "
            "structure that already failed, and do not trade the current error for one already "
            f"listed here:\n\n{chr(10).join(history)}\n"
            if len(history) > 1 else ""
        )
        prompt_context = context if attempt == 0 else (
            f"{context}{history_block}\n\nYour previous multi-file attempt:\n\n{_render_modelica_bundle(draft)}\n\n"
            f"Modelica preflight or the real OpenModelica compiler found these errors while checking the "
            f"real {understanding.simulation.stop_time:.0f}s scenario above:\n\n{errors_summary}\n\n"
            "Before patching: re-read the engineering brief above and work out WHY this error happened in "
            "terms of the actual physical/control behavior it's supposed to represent, not just the "
            "compiler's error text in isolation -- the same reported symptom can come from different real "
            "causes. A 'simulate() did not finish' / timeout result usually means event chattering "
            "(a `when`/`elsewhen` or `reinit` structure re-triggering itself near a boundary instead of "
            "settling) -- if you see that, reconsider the actual trigger/guard structure causing it, not a "
            "cosmetic patch. Fix the root cause, and never drop, weaken, or silently simplify away a "
            "required behavior (a timer reset, an interlock, a resume policy, a resolved parameter value) "
            "just to make the error go away -- if a fix would remove something the brief actually requires, "
            "find a different fix instead. Keep unrelated, already-correct parts of the model unchanged.\n\n"
            "Do not treat this as patching only the one reported line. Read the ENTIRE previous bundle "
            "above and, using your own full knowledge of real Modelica semantics (not just the specific "
            "errors listed), check every file for every other place the same class of mistake could "
            "also be present -- e.g. if one `reinit` was misplaced, check every `reinit` in the file; if "
            "one scheduled command wasn't genuinely one-shot, check every scheduled command; if one "
            "discrete variable had an ambiguous multi-writer definition, check every discrete variable. "
            "You have a limited number of attempts against the real compiler, so aim to return a file that "
            "passes on THIS attempt, not one that trades today's reported error for a different one next "
            "attempt."
        )
        with _traced_stage(f"Stage 3: write Modelica (attempt {attempt + 1}/{settings.max_repair_attempts + 1})", run_log):
            draft = reasoner.ask(modelica_prompt, prompt_context, ModelicaDraft, Packet([]))

        attempt_dir = _archive_modelica_attempt(ws, project_id, attempt + 1, draft)
        print(f"    [Stage 3] archived attempt {attempt + 1} at {attempt_dir}", flush=True)
        run_log.event("attempt_archived", stage=3, attempt=attempt + 1, path=str(attempt_dir))
        # A bundle with no `equation` section can't represent any real physics --
        # confirmed live: a draft returned a bare enum-only stub (its own
        # `corrections` text admitted it was a placeholder "to satisfy the tool-call
        # requirement"), which then trivially PASSED the real compiler because
        # there was nothing in it that could fail. Reject it before spending a real
        # compile/simulate attempt on something that was never going to be a real
        # model -- a compiler PASS is not evidence of completeness, only of syntax.
        bundle_text = _render_modelica_bundle(draft)
        if "equation" not in bundle_text:
            errors_summary = (
                "Your response was a stub -- the bundle declared no `equation` section at all, so it "
                "cannot represent any real physics or behavior no matter whether it compiles. "
                "Return the COMPLETE multi-file model: every state variable, every governing equation, "
                "every discrete transition the brief actually requires -- not a partial draft "
                "or placeholder."
            )
            print(f"    [Stage 3] draft has no equation section (stub), attempt {attempt + 1}: treating as failed", flush=True)
            run_log.event(
                "validation_attempt", stage=3, attempt=attempt + 1, tool="stub_check", status="FAILED",
                detail=errors_summary,
            )
            history.append(f"Attempt {attempt + 1} rejected (returned a stub with no equation section).")
            continue

        static_issues = _modelica_static_issues(draft, _checked_variable_names(understanding))
        blocking, advisory = _split_blocking(static_issues)
        if advisory:
            # Carried into the next attempt's context if there is one, so they
            # still get fixed, but never on their own account.
            print(
                f"    [Stage 3] preflight advisories (not blocking), attempt {attempt + 1}:\n"
                + "\n".join(advisory), flush=True,
            )
            run_log.event(
                "validation_attempt", stage=3, attempt=attempt + 1,
                tool="modelica_preflight", status="ADVISORY",
                error_count=len(advisory), errors="\n".join(advisory),
            )
        if blocking:
            errors_summary = "\n".join(blocking + advisory)
            print(
                f"    [Stage 3] Modelica preflight found {len(blocking)} blocking issue(s), "
                f"attempt {attempt + 1}:\n" + "\n".join(blocking), flush=True,
            )
            run_log.event(
                "validation_attempt", stage=3, attempt=attempt + 1,
                tool="modelica_preflight", status="FAILED",
                error_count=len(blocking), errors=errors_summary,
            )
            history.append(f"Attempt {attempt + 1} rejected by preflight:\n{errors_summary}")
            continue

        if not settings.use_real_compiler:
            break
        try:
            # `compile_files()`'s own defaults (stop_time=10.0, 10 intervals)
            # are DELIBERATELY a cheap structural sanity check, not a real
            # acceptance run (see that function's own docstring) -- found
            # live: leaving them unset here meant every Stage 3 repair
            # attempt only ever simulated the first 10s of this dataset's
            # 900s scenario, where nothing happens before the first
            # scheduled command at t=20s, so `PASSED` never actually proved
            # the model does anything. Use the brief's real simulation
            # window instead.
            result = compile_files(
                execution_id=f"{project_id}_attempt{attempt}", files=_draft_files(draft),
                entry_class=draft.entry_class, timeout=settings.omc_timeout_seconds,
                start_time=understanding.simulation.start_time, stop_time=understanding.simulation.stop_time,
                number_of_intervals=understanding.simulation.intervals, tolerance=understanding.simulation.tolerance,
            )
        except CompilerUnavailable as exc:
            print(f"    [Stage 3] real compiler unavailable, skipping validation: {exc}", flush=True)
            run_log.event("validation_attempt", stage=3, attempt=attempt + 1, tool="omc", status="UNAVAILABLE", detail=str(exc))
            break
        if result.status.value == "PASSED":
            # Compiling has never been the thing being judged. Stage 3 already
            # simulates the brief's real window here, so the trajectory is in
            # hand -- use it. A bundle whose reported quantities never move is
            # dead, and accepting it spends the remaining attempts on nothing
            # while Stage 4 discovers it later. Twice on this plant a model
            # compiled, ran the full 3000 s and left every level and
            # composition at its initial value; the second time two
            # temperatures sat at physically meaningless constants. Both were
            # accepted here and only caught downstream.
            dead = _inert_variables(result.result_summary, _checked_variable_names(understanding))
            if dead and attempt < settings.max_repair_attempts:
                errors_summary = (
                    f"The bundle compiles and simulates the full {understanding.simulation.stop_time:.0f}s "
                    f"window, but {', '.join(dead)} never change value for the entire run. A quantity an "
                    "acceptance check reads must actually move: the sequence has to start, the transfers "
                    "have to happen, and the states have to respond. Find what stops it -- a guard that can "
                    "never become true, a permissive wired to a constant, a flow that is never driven, a "
                    "stage whose exit condition is unreachable -- and fix that. Do not satisfy this by "
                    "forcing the values; the physics has to produce them."
                )
                print(
                    f"    [Stage 3] simulated but inert, attempt {attempt + 1}: "
                    f"{len(dead)} checked variable(s) never changed", flush=True,
                )
                run_log.event(
                    "validation_attempt", stage=3, attempt=attempt + 1, tool="omc",
                    status="INERT", error_count=len(dead), errors=errors_summary,
                )
                history.append(f"Attempt {attempt + 1} compiled but did nothing:\n{errors_summary}")
                continue
            if dead:
                print(
                    f"    [Stage 3] real omc: PASSED ({attempt + 1} attempt(s)) -- but "
                    f"{len(dead)} checked variable(s) never changed; no attempts left to fix it", flush=True,
                )
            else:
                print(f"    [Stage 3] real omc: PASSED ({attempt + 1} attempt(s))", flush=True)
            errors_summary = ""  # otherwise StageResult.remaining_errors would show a stale prior error
            run_log.event(
                "validation_attempt", stage=3, attempt=attempt + 1, tool="omc", status="PASSED",
                inert=sorted(dead) or None,
            )
            break
        errors_summary = "\n".join(f"- {e.file}:{e.line}: {e.message}" for e in result.errors)
        print(f"    [Stage 3] real omc found {len(result.errors)} error(s), attempt {attempt + 1}:\n{errors_summary}", flush=True)
        run_log.event(
            "validation_attempt", stage=3, attempt=attempt + 1, tool="omc", status="FAILED",
            error_count=len(result.errors), errors=errors_summary,
        )
        # Advisories ride along with a real rejection so they still get fixed,
        # marked as secondary so the attempt is spent on the compiler error.
        if advisory:
            errors_summary += (
                "\n\nAlso worth fixing while you are here, but none of these is why the attempt "
                "failed -- do not let them change the model's structure:\n" + "\n".join(advisory)
            )
        history.append(f"Attempt {attempt + 1} rejected by the real OpenModelica compiler:\n{errors_summary}")

    generated_dir = _modelica_generated_dir(ws, project_id)
    generated_dir.mkdir(parents=True, exist_ok=True)
    current_names = {file.filename for file in draft.files}
    # A rerun replaces the bundle as a unit. Stale component files can otherwise
    # appear in OMEdit and in the API even though Stage 4 did not compile them.
    for stale in generated_dir.glob("*.mo"):
        if stale.name not in current_names:
            stale.unlink()
    written: list[Path] = []
    for file in draft.files:
        path = generated_dir / file.filename
        path.write_text(file.code, encoding="utf-8")
        written.append(path)
    _modelica_manifest_path(ws, project_id).write_text(
        json.dumps({
            "entry_class": draft.entry_class,
            "files": [file.model_dump(exclude={"code"}) for file in draft.files],
            "library_components": draft.library_components,
            "corrections": draft.corrections,
            "references": [r.model_dump() for r in draft.references],
        }, indent=2), encoding="utf-8",
    )

    if errors_summary:
        raise RuntimeError(
            "Stage 3 exhausted its OpenModelica repair attempts; the last bundle was saved for inspection "
            f"but is not validated:\n{errors_summary}"
        )

    return StageResult(
        stage="stage_3", project_id=project_id, status="READY",
        details={
            "entry_class": draft.entry_class,
            "files": [str(path) for path in written],
            "code_chars": sum(len(file.code) for file in draft.files),
            "library_components": draft.library_components,
            "corrections": draft.corrections,
            "remaining_errors": errors_summary or None,
        },
    )


def _modelica_results_dir(ws: Workspace, project_id: str) -> Path:
    return ws.modelica_dir(project_id) / "results"


def _load_modelica_bundle(ws: Workspace, project_id: str) -> tuple[str, dict[str, str], list[str]]:
    """Load the exact ordered bundle Stage 3 compiled.

    A legacy one-file fallback keeps projects generated before the bundle
    manifest was introduced readable and re-validatable.
    """

    generated_dir = _modelica_generated_dir(ws, project_id)
    manifest_path = _modelica_manifest_path(ws, project_id)
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        files: dict[str, str] = {}
        for item in manifest.get("files", []):
            filename = item["filename"]
            path = generated_dir / filename
            if not path.exists():
                raise FileNotFoundError(f"Modelica bundle file listed in manifest is missing: {filename}")
            files[filename] = path.read_text(encoding="utf-8")
        if not files:
            raise ValueError(f"Modelica manifest for project {project_id!r} contains no files")
        return manifest["entry_class"], files, manifest.get("corrections", [])

    legacy_files = sorted(generated_dir.glob("*.mo"), key=lambda p: p.stat().st_mtime) if generated_dir.exists() else []
    if not legacy_files:
        raise FileNotFoundError(f"No generated Modelica files for project {project_id!r} -- run Stage 3 first.")
    path = legacy_files[-1]
    corrections: list[str] = []
    legacy_meta = generated_dir / f"{path.stem}.meta.json"
    if legacy_meta.exists():
        try:
            corrections = json.loads(legacy_meta.read_text(encoding="utf-8")).get("corrections", [])
        except (json.JSONDecodeError, OSError):
            pass
    return path.stem, {path.name: path.read_text(encoding="utf-8")}, corrections


def _render_trajectory_digest(
    csv_path: Path, summary: dict[str, dict[str, float]], max_distinct: int = 25, max_lines: int = 400,
) -> str:
    """Real simulated data for Stage 4 -- never the generating model's own
    self-report. Two views: (1) min/max/final for every variable (from the
    real compiler run), which alone hides exactly the kind of bug this
    project's own discipline has repeatedly found live -- a variable that
    is 'individually plausible' in isolation but never actually completes
    its intended transition; and (2) a real event trace of every
    discrete/step-like variable (few distinct values across the whole run)
    showing exactly WHEN it changed and to what. That second view is the
    same manual technique ('track prev_mode, print on change') this session
    used by hand to catch a batch process silently stuck in one phase for
    the entire run despite a real, non-stub, compiler-PASSED result --
    codified here instead of redone ad hoc every time."""

    lines = ["Real simulated result summary (min/max/final per variable, from an actual omc simulate()):"]
    for name in sorted(summary):
        s = summary[name]
        lines.append(f"  {name}: min={s['min']:.6g} max={s['max']:.6g} final={s['final']:.6g}")

    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        return "\n".join(lines)

    header = reader.fieldnames or []
    time_col = "time" if "time" in header else header[0]

    change_log_lines: list[str] = []
    for col in header:
        if col == time_col:
            continue
        try:
            values = [float(r[col]) for r in rows]
        except (ValueError, KeyError):
            continue
        distinct = sorted({round(v, 6) for v in values})
        if len(distinct) > max_distinct:
            continue  # a genuinely continuous variable -- the summary above already covers it
        prev = None
        changes = []
        for row, v in zip(rows, values):
            rv = round(v, 6)
            if rv != prev:
                changes.append(f"    t={row[time_col]}: {col} = {rv:g}")
                prev = rv
        if len(changes) > 1:  # skip variables that never actually change
            change_log_lines.extend(changes)

    if change_log_lines:
        lines.append("\nWhen each discrete/step-like variable actually changed value (real event trace):")
        lines.extend(change_log_lines[:max_lines])
        if len(change_log_lines) > max_lines:
            lines.append(f"  ... ({len(change_log_lines) - max_lines} more change(s) truncated)")
    return "\n".join(lines)


def _plot_trajectory(csv_path: Path, out_dir: Path, model_name: str, max_series: int = 24) -> list[Path]:
    """Saves each changing simulated variable as its own PNG line plot for
    the HUMAN reading Stage 4's result -- not for the LLM (vision
    stays off this project's own standing choice, see `_understand_documents`'s
    docstring; Stage 4's review is grounded in `_render_trajectory_digest`'s
    real numbers, not a picture). matplotlib directly against the CSV
    `compile_files()` already writes -- the same approach already used by
    hand this session for the tank_v3/magnet_v3 plots; no OMPython or other
    new simulation-layer dependency needed on top of this project's own
    hardened `compile_files()` compiler wrapper. Skips any column that never
    changes (a fixed parameter echoed into the CSV) -- a flat line shows
    nothing. Limits the set rather than silently creating an unbounded number
    of images. Returns the list of individual files written (empty if nothing
    changes)."""

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        return []
    header = reader.fieldnames or []
    time_col = "time" if "time" in header else header[0]
    times = [float(r[time_col]) for r in rows]

    series: dict[str, list[float]] = {}
    for col in header:
        if col == time_col:
            continue
        try:
            values = [float(r[col]) for r in rows]
        except (ValueError, KeyError):
            continue
        if max(values) - min(values) < 1e-12:
            continue
        series[col] = values
    if not series:
        return []

    out_dir.mkdir(parents=True, exist_ok=True)
    names = sorted(series)[:max_series]
    written: list[Path] = []
    for stale in out_dir.glob(f"{model_name}.trajectory*.png"):
        stale.unlink()
    for index, name in enumerate(names, 1):
        fig, ax = plt.subplots(figsize=(9, 4.8))
        ax.plot(times, series[name], linewidth=1.5)
        ax.set_title(name, fontsize=11)
        ax.set_xlabel("time")
        ax.set_ylabel(name)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")[:80] or f"series_{index}"
        out_path = out_dir / f"{model_name}.trajectory.{index:02d}.{safe_name}.png"
        fig.savefig(out_path, dpi=130)
        plt.close(fig)
        written.append(out_path)
    return written


def execute_reasoner_stage_4(project_id: str, projects_root: Path | None = None) -> StageResult:
    """Independent result validation -- runs AFTER Stage 3 has a Modelica
    file that passes the real compiler. Re-simulates it for real (same
    `compile_files`, same brief-derived simulation window Stage 3 itself
    validates against), saves the real CSV/summary/plots, then hands an
    LLM the REAL numbers plus the actual problem statement (never the
    generating model's own self-report) and asks for an honest verdict:
    is this actually right, what's wrong, what did we assume, and why did
    it come out this way.

    This is the same check this project's own established discipline has
    required doing BY HAND all session ('never trust a bare PASSED') --
    codified as its own stage so it happens for every project automatically,
    not only when someone remembers to ask for it."""

    from simulation_platform.tools import CompilerUnavailable, compile_files

    ws = _workspace(projects_root)
    run_log = RunLog(ws.run_log_path(project_id))
    settings = PlatformSettings.load()
    understanding = _load_merged_understanding(ws, project_id)

    model_name, modelica_files, stage3_corrections = _load_modelica_bundle(ws, project_id)

    results_dir = _modelica_results_dir(ws, project_id)
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / f"{model_name}.csv"

    with _traced_stage("Stage 4: re-simulate for real and save the result", run_log):
        try:
            result = compile_files(
                execution_id=f"{project_id}_stage4", files=modelica_files, entry_class=model_name,
                timeout=settings.omc_timeout_seconds, start_time=understanding.simulation.start_time,
                stop_time=understanding.simulation.stop_time, number_of_intervals=understanding.simulation.intervals,
                tolerance=understanding.simulation.tolerance, result_csv_path=csv_path,
            )
        except CompilerUnavailable as exc:
            print(f"    [Stage 4] real compiler unavailable, cannot validate: {exc}", flush=True)
            run_log.event("validation_attempt", stage=4, tool="omc", status="UNAVAILABLE", detail=str(exc))
            return StageResult(
                stage="stage_4", project_id=project_id, status="SKIPPED",
                details={"reason": f"real compiler unavailable: {exc}"},
            )

    plot_paths: list[Path] = []
    if result.status.value == "PASSED":
        summary_path = results_dir / f"{model_name}.summary.json"
        summary_path.write_text(json.dumps(result.result_summary, indent=2), encoding="utf-8")
        with _traced_stage("Stage 4: plot the real trajectory", run_log):
            plot_paths = _plot_trajectory(csv_path, results_dir, model_name)

        digest = _render_trajectory_digest(csv_path, result.result_summary)
        context = "\n\n".join([
            _understanding_context(understanding, _load_clarified_answers(ws, project_id)),
            "Assumptions the model-generation stage explicitly made while writing this Modelica model:\n"
            + ("\n".join(f"- {c}" for c in stage3_corrections) if stage3_corrections else "(none recorded)"),
            digest,
        ])

        reasoner = Reasoner(settings, 4, backend="openai", run_log=run_log)
        with _traced_stage("Stage 4: independent review of the real result against the brief", run_log):
            report: ValidationReport = reasoner.ask(VALIDATION, context, ValidationReport, Packet([]))
    else:
        errors_summary = "\n".join(f"- {e.file}:{e.line}: {e.message}" for e in result.errors)
        print(f"    [Stage 4] real omc did not pass, skipping trajectory review:\n{errors_summary}", flush=True)
        run_log.event("validation_attempt", stage=4, tool="omc", status="FAILED", errors=errors_summary)
        report = ValidationReport(
            verdict="invalid",
            summary=(
                "The generated Modelica model does not compile/simulate cleanly against the real omc "
                "compiler, so there is no result to validate against the problem statement."
            ),
            issues=[f"Real omc simulate() failed: {errors_summary}"],
            assumptions=[],
            root_causes=["Stage 3's output did not pass the real compiler -- see Stage 3's own remaining_errors."],
        )

    validation_dir = ws.validation_dir(project_id)
    validation_dir.mkdir(parents=True, exist_ok=True)
    report_path = validation_dir / f"{model_name}.report.json"
    # A rerun whose entry class was renamed used to leave the previous run's
    # report sitting beside the new one, with no indication which was current --
    # confirmed live: a stale report was read as this run's result and described
    # a trajectory the current model never produced. Stage 3 already prunes its
    # own stale .mo files for the same reason; do the same here.
    for stale in validation_dir.glob("*.report.json"):
        if stale != report_path:
            stale.unlink()
    report_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")

    run_log.event("validation_report", stage=4, verdict=report.verdict, issue_count=len(report.issues))

    return StageResult(
        stage="stage_4", project_id=project_id, status="READY",
        details={
            "report_file": str(report_path), "verdict": report.verdict, "summary": report.summary,
            "issues": report.issues, "assumptions": report.assumptions, "root_causes": report.root_causes,
            "csv": str(csv_path) if result.status.value == "PASSED" else None,
            "plots": [str(p) for p in plot_paths],
        },
    )
