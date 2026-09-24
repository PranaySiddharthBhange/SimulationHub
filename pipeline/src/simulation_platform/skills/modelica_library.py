"""Searchable catalogue of the installed Modelica Standard Library.

`data/modelica_catalog.json` holds the component entries, the whole-system
reference models, and the do/don't rules. Every class named in it was confirmed
present by querying the installed library with `omc`, which is the point of
keeping it as data: a prose catalogue written from memory cannot be re-checked
against an installation, and a class that does not exist fails at compile time
with an error that reads like a syntax mistake.

Two ways in, because the stages need different things:

- `lookup(query, domains=...)` answers "what do I use for a pump?" -- a
  keyword search for a reader who knows what they want to build.
- `catalog_block(domains)` renders the slice for a set of domains as prompt
  text, which is what Stage 3 receives.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_CATALOG_PATH = Path(__file__).parent / "data" / "modelica_catalog.json"


@lru_cache(maxsize=1)
def catalog() -> dict:
    return json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))


def _matches(entry: dict, terms: list[str]) -> int:
    """How well one entry answers the query. 0 means it does not."""

    haystack = " ".join([
        entry["class"], entry.get("use_for", ""),
        " ".join(entry.get("keywords", [])), entry.get("note", ""),
    ]).lower()
    # The class name is what someone searching for "OpenTank" actually typed,
    # so a hit there outranks the same word appearing in a description.
    return sum(3 if term in entry["class"].lower() else 1 for term in terms if term in haystack)


def lookup(query: str, domains: list[str] | None = None, limit: int = 8) -> list[dict]:
    """Components answering `query`, best first, optionally within `domains`."""

    terms = [t for t in query.lower().split() if t]
    entries = catalog()["components"]
    if domains:
        wanted = set(domains)
        entries = [e for e in entries if wanted & set(e.get("domains", []))] or entries
    scored = [(_matches(e, terms), e) for e in entries]
    return [e for score, e in sorted(scored, key=lambda p: -p[0]) if score > 0][:limit]


def reference_models(domains: list[str] | None = None) -> list[dict]:
    models = catalog()["reference_models"]
    if not domains:
        return models
    # A reference model is worth showing when any class it uses serves one of
    # this system's domains -- matching on the case description alone would
    # miss a plant whose wording differs from the catalogue's.
    by_class = {c["class"]: set(c.get("domains", [])) for c in catalog()["components"]}
    wanted = set(domains)
    return [m for m in models if any(wanted & by_class.get(c, set()) for c in m["verified_uses"])]


def _render_component(entry: dict) -> str:
    lines = [f"- {entry['class']}: {entry['use_for']}"]
    if entry.get("key_parameters"):
        lines.append(f"    parameters: {', '.join(entry['key_parameters'])}")
    if entry.get("ports"):
        lines.append(f"    ports: {'; '.join(entry['ports'])}")
    if entry.get("note"):
        lines.append(f"    note: {entry['note']}")
    return "\n".join(lines)


def catalog_block(domains: list[str]) -> str:
    """The catalogue slice for `domains`, as prompt text.

    Returns "" for no matching domain rather than the whole library: an
    unrecognised domain should degrade to no extra guidance, never to every
    component in the standard library.
    """

    data = catalog()
    wanted = set(domains)
    components = [c for c in data["components"] if wanted & set(c.get("domains", []))]
    if not components:
        return ""

    models = reference_models(domains)
    out = [
        f"MODELICA STANDARD LIBRARY {data['modelica_standard_library']} -- VERIFIED CATALOGUE",
        "",
        data["verified"],
        "",
    ]
    if models:
        out += ["WHOLE-SYSTEM PATTERNS. When one of these matches the shape of this system, follow it:", ""]
        for model in models:
            out.append(f"- {model['msl_model']}")
            out.append(f"    for: {model['case']}")
            out.append(f"    shape: {model['shape']}")
            out.append(f"    built from: {', '.join(model['verified_uses'])}")
            # The parameter VALUES are the part that decides whether the model
            # builds at all -- a valve with dp_nominal = 0 fails where 1 Pa
            # works -- so the skeleton is read out of the installed example
            # rather than left for the model to guess.
            for note in model.get("parameterisation", []):
                out.append(f"    - {note}")
            if model.get("verified_skeleton"):
                out.append("")
                out.append("    How that example is actually written, read out of the installed library:")
                out.append("")
                out += [f"      {line}" for line in model["verified_skeleton"].splitlines()]
            out.append("")

    out += [f"COMPONENTS for this system's domains ({', '.join(sorted(wanted))}):", ""]
    out += [_render_component(c) for c in components]
    out += ["", "RULES -- these hold in every domain.", "", "Do:"]
    for rule in data["rules"]["do"]:
        out.append(f"- {rule['rule']}")
        out.append(f"    why: {rule['why']}")
        if rule.get("evidence"):
            out.append(f"    seen live: {rule['evidence']}")
    out += ["", "Do not:"]
    for rule in data["rules"]["dont"]:
        out.append(f"- {rule['rule']}")
        out.append(f"    why: {rule['why']}")
        if rule.get("evidence"):
            out.append(f"    seen live: {rule['evidence']}")
    return "\n".join(out) + "\n"


def _main() -> int:
    """Search the catalogue from a terminal:

        python -m simulation_platform.skills.modelica_library pump
        python -m simulation_platform.skills.modelica_library --domain magnetic_circuit leakage
    """

    import argparse

    parser = argparse.ArgumentParser(description="Search the verified Modelica catalogue.")
    parser.add_argument("query", nargs="+", help="what you are trying to model")
    parser.add_argument("--domain", action="append", default=[], help="restrict to a domain key (repeatable)")
    args = parser.parse_args()

    hits = lookup(" ".join(args.query), domains=args.domain or None)
    if not hits:
        print("no match; try a broader word, or run with no --domain")
        return 1
    for entry in hits:
        print(_render_component(entry))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
