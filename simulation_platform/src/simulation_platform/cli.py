"""CLI entry point. See `new direction.txt` §2-3, §32:

    simulation-platform run      --problem problem.md --docs ./documents/
    simulation-platform index    --problem problem.md --docs ./documents/
    simulation-platform sysml    --project <id>
    simulation-platform simulate --project <id>
    simulation-platform status   --project <id>
    simulation-platform inspect  --project <id>

`run` has no logic of its own -- it calls the exact same `pipeline.py`
functions the individual stage commands call (see that module's own
docstring). This file's only jobs are: parse arguments, drive the shared
human-in-the-loop interrupt loop interactively (§14), and print results.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import openai

from simulation_platform import pipeline
from simulation_platform.tools.knowledge_search import search_project


class InteractiveInputUnavailable(RuntimeError):
    """Raised when this stage genuinely needs a human decision (an
    ambiguity, or an unconfirmed value) but stdin has no real interactive
    terminal behind it (`input()` hit EOF immediately). Found live: running
    non-interactively crashed with a raw `EOFError` traceback instead of a
    clean message -- but silently defaulting to "accept everything" here
    would be worse, since it would rubber-stamp exactly the kind of
    unconfirmed decision `new direction.txt` §15 says must never be
    applied without a real human answer. The one exception is a plain
    acknowledgment (`human_review`'s "press Enter to continue") -- nothing
    is actually decided there, so EOF is harmless to treat as "proceed."
    """


def _prompt(text: str) -> str:
    try:
        return input(text)
    except EOFError as exc:
        raise InteractiveInputUnavailable(
            "This stage paused for a real human decision, but no interactive terminal is available "
            "(stdin hit EOF). Re-run this command in an interactive terminal so you can actually answer it."
        ) from exc


def _interactive_on_interrupt(project_id: str) -> pipeline.OnInterrupt:
    def handle(payload: dict) -> object:
        # Stage 1: one or more high-impact ambiguities need a human answer.
        if "pending_ambiguities" in payload:
            project_dir = pipeline.workspace().project_dir(project_id)
            answers = []
            for amb in payload["pending_ambiguities"]:
                print(f"\nAmbiguity {amb['ambiguity_id']}: {amb['question']}")
                if amb.get("candidates"):
                    print(f"  Candidates: {', '.join(str(c) for c in amb['candidates'])}")
                hits = search_project(project_dir, amb["question"], max_results=3)
                for hit in hits:
                    print(f"  [{hit['source']}] {hit['text'][:160]}")
                answer = _prompt("  Your answer (or a candidate above): ").strip()
                answers.append({"ambiguity_id": amb["ambiguity_id"], "answer": answer})
            return answers

        # Stage 3: a value this pipeline could not derive on its own (a
        # never-assigned legacy variable, a generic library placeholder, a
        # parameter with no requirement bound, or a from-scratch stub's
        # sensed field) -- an LLM has already proposed a grounded
        # suggestion (see `mapping/parameter_value_suggester.py`); it's
        # never applied unconfirmed (`new direction.txt` §15). Pressing
        # Enter accepts the suggestion verbatim; typing a real Modelica
        # expression overrides it; typing "skip" leaves it as the inert
        # default, unconfirmed, so a future run will ask again rather than
        # silently keep guessing.
        if "pending_value_decisions" in payload:
            answers = []
            for decision in payload["pending_value_decisions"]:
                print(f"\n{decision['class_name']}.{decision['variable']}: {decision['reason']}")
                print(f"  Suggested: {decision['suggested_value']}")
                raw = _prompt("  Accept [Enter], type a replacement expression, or 'skip': ").strip()
                if raw.lower() == "skip":
                    answers.append(None)
                elif raw:
                    answers.append(raw)
                else:
                    answers.append(decision["suggested_value"])
            return answers

        # Stage 2/3: validation or compile failed after exhausting auto-repair.
        report_path = payload.get("validation_report_path")
        print(f"\nStage needs human review. Report: {report_path}")
        if report_path and Path(report_path).exists():
            print(Path(report_path).read_text(encoding="utf-8")[:2000])
        if payload.get("compile_status"):
            print(f"Compile status: {payload['compile_status']}")
        # Nothing is actually decided here (the value is discarded either
        # way) -- unlike the other two cases above, EOF is safe to treat
        # as "proceed" rather than raise.
        try:
            input("Press Enter to acknowledge and continue (the run is recorded either way): ")
        except EOFError:
            print("(no interactive terminal available; proceeding without waiting for input)")
        # NEVER a bare `None` -- found live: a real `langgraph` 1.2.11 bug
        # (`pregel/_loop.py`'s `_first`) only assigns its own internal
        # `resume_is_map` variable inside `if resume is not None`, so
        # `Command(resume=None)` crashes with a raw `UnboundLocalError`
        # for ANY caller, unrelated to anything specific to this platform.
        # `human_review_node` never reads what it resumes with anyway
        # (it just returns a fixed `{"status": "REVIEWED"}`), so any
        # non-None placeholder is exactly as correct as `None` was meant
        # to be, and avoids tripping the library bug.
        return "acknowledged"

    return handle


def _print_stage_result(result: pipeline.StageResult) -> None:
    mark = "✓" if result.status == "READY" else "✗"
    print(f"{result.stage}: {result.status} {mark}")


def _cmd_index(args: argparse.Namespace) -> int:
    project_id = args.project or Path(args.docs).resolve().name
    result = pipeline.execute_stage_1(
        project_id,
        problem_path=Path(args.problem) if args.problem else None,
        docs_dir=Path(args.docs) if args.docs else None,
        on_interrupt=_interactive_on_interrupt(project_id),
        force=args.force,
    )
    _print_stage_result(result)
    if result.details.get("skipped"):
        print("  (skipped -- input unchanged since last completed run; use --force to rerun)")
    return 0 if result.status == "READY" else 1


def _cmd_sysml(args: argparse.Namespace) -> int:
    result = pipeline.execute_stage_2(args.project, on_interrupt=_interactive_on_interrupt(args.project), force=args.force)
    _print_stage_result(result)
    if result.details.get("skipped"):
        print("  (skipped -- input unchanged since last completed run; use --force to rerun)")
    return 0 if result.status == "READY" else 1


def _cmd_simulate(args: argparse.Namespace) -> int:
    result = pipeline.execute_stage_3(args.project, on_interrupt=_interactive_on_interrupt(args.project), force=args.force)
    _print_stage_result(result)
    if result.details.get("skipped"):
        print("  (skipped -- input unchanged since last completed run; use --force to rerun)")
    return 0 if result.status == "READY" else 1


def _cmd_run(args: argparse.Namespace) -> int:
    project_id = args.project or (Path(args.docs).resolve().name if args.docs else None)
    if not project_id:
        print("error: --project or --docs is required", file=sys.stderr)
        return 2

    results = pipeline.run_full_pipeline(
        project_id,
        problem_path=Path(args.problem) if args.problem else None,
        docs_dir=Path(args.docs) if args.docs else None,
        on_interrupt=_interactive_on_interrupt(project_id),
        force=args.force,
    )

    print("\nPipeline completed.\n")
    for result in results:
        _print_stage_result(result)

    all_ready = all(r.status == "READY" for r in results)
    if all_ready:
        summary = pipeline.stage_status_summary(project_id)
        print(f"\nProject: {project_id}")
        compile_status = summary.get("compile_status")
        print(f"Simulation: {compile_status if compile_status else 'not run'}")
        report = summary.get("result_validation")
        if report:
            print(f"Result validation: {report['status']}")
            for issue in report.get("issues", []):
                print(f"  ! {issue}")
    return 0 if all_ready else 1


def _cmd_status(args: argparse.Namespace) -> int:
    import json

    summary = pipeline.stage_status_summary(args.project)
    print(json.dumps(summary, indent=2))
    return 0


def _cmd_inspect(args: argparse.Namespace) -> int:
    path = pipeline.workspace().system_model_path(args.project)
    if not path.exists():
        print(f"No system model yet for project {args.project!r} — run `index` first.", file=sys.stderr)
        return 1
    print(path.read_text(encoding="utf-8"))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="simulation-platform")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_run = subparsers.add_parser("run", help="execute the full pipeline (Stage 1 -> 2 -> 3)")
    p_run.add_argument("--problem", help="path to problem.md")
    p_run.add_argument("--docs", help="path to a documents folder")
    p_run.add_argument("--project", help="project id (defaults to the --docs folder name)")
    p_run.add_argument("--force", action="store_true", help="rerun every stage even if its input hasn't changed")
    p_run.set_defaults(func=_cmd_run)

    p_index = subparsers.add_parser("index", help="Stage 1 only: Document Indexing")
    p_index.add_argument("--problem", help="path to problem.md")
    p_index.add_argument("--docs", help="path to a documents folder")
    p_index.add_argument("--project", help="project id (defaults to the --docs folder name)")
    p_index.add_argument("--force", action="store_true", help="rerun even if input hasn't changed since last run")
    p_index.set_defaults(func=_cmd_index)

    p_sysml = subparsers.add_parser("sysml", help="Stage 2 only: SysML v2 Generation")
    p_sysml.add_argument("--project", required=True)
    p_sysml.add_argument("--force", action="store_true", help="rerun even if input hasn't changed since last run")
    p_sysml.set_defaults(func=_cmd_sysml)

    p_simulate = subparsers.add_parser("simulate", help="Stage 3 only: Modelica Generation + Simulation + Validation")
    p_simulate.add_argument("--project", required=True)
    p_simulate.add_argument("--force", action="store_true", help="rerun even if input hasn't changed since last run")
    p_simulate.set_defaults(func=_cmd_simulate)

    p_status = subparsers.add_parser("status", help="show per-stage status for a project")
    p_status.add_argument("--project", required=True)
    p_status.set_defaults(func=_cmd_status)

    p_inspect = subparsers.add_parser("inspect", help="print the central resolved system model")
    p_inspect.add_argument("--project", required=True)
    p_inspect.set_defaults(func=_cmd_inspect)

    return parser


def _ensure_utf8_streams() -> None:
    """Found live on a real Windows run: this CLI prints real Unicode (the
    ✓/✗ marks in `_print_stage_result`, and potentially non-ASCII content
    quoted straight from a source document) but Windows' default console
    codepage (cp1252) can't encode it -- a real run crashed with
    `UnicodeEncodeError` AFTER the actual pipeline work had already
    completed successfully, just trying to print the result. `reconfigure`
    itself never raises for an unsupported/missing case (e.g. stdout/
    stderr redirected to something that doesn't implement it) -- guarded
    here anyway since that guarantee lives in CPython's implementation,
    not in the method's own documented contract."""

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def main(argv: list[str] | None = None) -> int:
    _ensure_utf8_streams()

    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (RuntimeError, openai.OpenAIError) as exc:
        # Covers every "expected, actionable" failure this platform raises
        # deliberately (ExtractionUnavailable/LLMUnavailable/BudgetExceeded/
        # ConfigError -- all RuntimeError subclasses) PLUS a real failure
        # from the OpenAI API itself (auth, rate limit, and -- found live
        # while auditing this before a real-key test run -- an invalid
        # model name: `openai.NotFoundError`/`BadRequestError`/`APIError`
        # all inherit from `openai.OpenAIError`, not `RuntimeError`, so a
        # typo'd `STAGE_N_..._MODEL` in `.env` previously surfaced as a raw
        # traceback instead of this same clean one-line message. Anything
        # else is a real bug and should still show its traceback.
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
