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
    Stage 2: read ALL of Stage 1's per-document understanding files ->
             write the SysML v2 file directly (`contracts.SysMLDraft.code`),
             one call, no separate planning/mapping/validation calls.
    Stage 3: read the merged understanding + concise SysML flow -> write an
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
    Check, Clarification, ModelicaDraft, Simulation, SysMLDraft, Understanding, ValidationReport,
)
from simulation_platform.project_store import ProjectStore
from simulation_platform.reasoner import Reasoner
from simulation_platform.prompts.merge_notes import MERGE_PROMPT
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


def _modelica_static_issues(draft: ModelicaDraft) -> list[str]:
    """Catch deterministic Modelica mistakes before spending an omc run.

    `connect()` accepts connectors only. Generated bundles have repeatedly used
    ordinary Boolean/Real/Integer variables as endpoints, even though those
    values must be assigned with equations instead.
    """

    declaration = re.compile(
        r"(?m)^\s*(?:(?:parameter|constant|discrete|input|output)\s+)*"
        r"(?:Real|Boolean|Integer)\s+([^;]+);"
    )
    connection = re.compile(
        r"\bconnect\s*\(\s*([^,()]+?)\s*,\s*([^,()]+?)\s*\)", re.MULTILINE,
    )
    issues: list[str] = []
    for file in draft.files:
        plain_scalars: set[str] = set()
        for match in declaration.finditer(file.code):
            for item in match.group(1).split(","):
                name_match = re.match(r"\s*([A-Za-z_]\w*)", item)
                if name_match:
                    plain_scalars.add(name_match.group(1))
        for match in connection.finditer(file.code):
            for endpoint in (match.group(1).strip(), match.group(2).strip()):
                bare = re.fullmatch(r"([A-Za-z_]\w*)(?:\[[^\]]+\])?", endpoint)
                if bare and bare.group(1) in plain_scalars:
                    line = file.code.count("\n", 0, match.start()) + 1
                    issues.append(
                        f"- {file.filename}:{line}: connect() endpoint '{endpoint}' is an ordinary scalar, "
                        "not a connector. Replace the connection with an equation assignment or use a "
                        "proper Modelica connector."
                    )
    return issues


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

        if is_image_only:
            packet = Packet([source])
            text = reasoner.ask_free_text(DOCUMENT_UNDERSTANDING_PROMPT, "", packet)
            out_path = understanding_dir / f"{doc_index}_{doc_path.stem}.txt"
            out_path.write_text(text, encoding="utf-8")
            written.append(out_path)
            print(f"    [Stage 1:{backend}] document {doc_index}/{len(doc_paths)}: {rel} (visual)", flush=True)
            continue

        chunks = _chunk_source_text(source.text) if len(source.text) > _MAX_CHARS_PER_CHUNK else [source.text]
        for chunk_index, chunk_text in enumerate(chunks):
            chunk_source = Source(rel, chunk_text, images=[])
            packet = Packet([chunk_source])
            label = f"{rel}" + (f" (chunk {chunk_index + 1}/{len(chunks)})" if len(chunks) > 1 else "")
            print(f"    [Stage 1:{backend}] document {doc_index}/{len(doc_paths)}: {label}", flush=True)
            text = reasoner.ask_free_text(DOCUMENT_UNDERSTANDING_PROMPT, "", packet)
            suffix = f"_chunk{chunk_index:02d}" if len(chunks) > 1 else ""
            out_path = understanding_dir / f"{doc_index:02d}_{doc_path.stem}{suffix}.txt"
            out_path.write_text(text, encoding="utf-8")
            written.append(out_path)

    return written

def _load_all_understanding(ws: Workspace, project_id: str) -> str:
    files = sorted(_understanding_dir(ws, project_id).glob("*.txt"))
    return "\n\n".join(f"--- {p.name} ---\n{p.read_text(encoding='utf-8')}" for p in files)


def _merged_understanding_path(ws: Workspace, project_id: str) -> Path:
    return ws.extracted_dir(project_id) / "merged_understanding.json"


def _merged_narrative_path(ws: Workspace, project_id: str) -> Path:
    return ws.extracted_dir(project_id) / "merged_understanding.txt"


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


def _understanding_context(understanding: Understanding) -> str:
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
            "Open questions Merge flagged as unresolved (informational -- Stage 2 may raise its own "
            "`clarifications` for anything here that materially affects the model):\n"
            + "\n".join(f"- {q}" for q in understanding.questions)
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
    _merged_narrative_path(ws, project_id).write_text(understanding.narrative, encoding="utf-8")

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

    Human-in-the-loop, Stage 2 ONLY (the user's explicit choice -- Stage 1
    and Stage 3 stay fully autonomous): the first draft may also surface a
    handful of `clarifications` (see `contracts.Clarification`) for a
    decision the brief left genuinely open. When `clarify` is given, those
    are handed to it -- e.g. the API layer pauses the run and waits for a
    person to pick an answer (or accept the model's own `suggested_value`)
    -- and the model rewrites the draft once with the confirmed answers
    before the real-parser repair loop begins. `clarify=None` (the default,
    used by tests and any non-interactive caller) skips this entirely: the
    draft already used its own `suggested_value` for every open item, so
    the pipeline never blocks on a human who isn't there."""

    from simulation_platform.tools import RealParserUnavailable, validate_files_with_real_parser

    ws = _workspace(projects_root)
    run_log = RunLog(ws.run_log_path(project_id))
    settings = PlatformSettings.load()
    understanding = _load_merged_understanding(ws, project_id)
    context = _understanding_context(understanding)
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

    context = f"{_understanding_context(understanding)}\n\nSysML v2 model (already generated):\n\n{sysml_code}"
    modelica_prompt = (
        MODELICA
        + domain_skill_block(understanding.domains)
        + modelica_catalog_block(understanding.domains)
    )
    reasoner = Reasoner(settings, 3, backend="openai", run_log=run_log)
    draft: ModelicaDraft | None = None
    errors_summary = ""

    for attempt in range(settings.max_repair_attempts + 1):
        prompt_context = context if attempt == 0 else (
            f"{context}\n\nYour previous multi-file attempt:\n\n{_render_modelica_bundle(draft)}\n\n"
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
            continue

        static_issues = _modelica_static_issues(draft)
        if static_issues:
            errors_summary = "\n".join(static_issues)
            print(
                f"    [Stage 3] Modelica preflight found {len(static_issues)} invalid connect endpoint(s), "
                f"attempt {attempt + 1}:\n{errors_summary}", flush=True,
            )
            run_log.event(
                "validation_attempt", stage=3, attempt=attempt + 1,
                tool="modelica_preflight", status="FAILED",
                error_count=len(static_issues), errors=errors_summary,
            )
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
            print(f"    [Stage 3] real omc: PASSED ({attempt + 1} attempt(s))", flush=True)
            errors_summary = ""  # otherwise StageResult.remaining_errors would show a stale prior error
            run_log.event("validation_attempt", stage=3, attempt=attempt + 1, tool="omc", status="PASSED")
            break
        errors_summary = "\n".join(f"- {e.file}:{e.line}: {e.message}" for e in result.errors)
        print(f"    [Stage 3] real omc found {len(result.errors)} error(s), attempt {attempt + 1}:\n{errors_summary}", flush=True)
        run_log.event(
            "validation_attempt", stage=3, attempt=attempt + 1, tool="omc", status="FAILED",
            error_count=len(result.errors), errors=errors_summary,
        )

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
            _understanding_context(understanding),
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
