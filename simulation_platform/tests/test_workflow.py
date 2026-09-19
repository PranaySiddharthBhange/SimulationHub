from dataclasses import replace
from types import SimpleNamespace

import pytest

from simulation_platform import pipeline
from simulation_platform.cli import main
from simulation_platform.config import PlatformSettings
from simulation_platform.contracts import Check, ModelicaDraft, Review, Simulation, SysMLDraft, Understanding
from simulation_platform.schemas.compiler_result import CompileResult, CompileStatus


@pytest.fixture
def engine(tmp_path, monkeypatch):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "requirements.txt").write_text("A state begins at zero and must reach ten after ten seconds.")
    (docs / "physics.txt").write_text("The state changes at one unit per second; initial value is zero.")
    settings = replace(PlatformSettings.load(), projects_root=tmp_path / "projects", max_repair_attempts=0,
                       use_real_compiler=True, use_real_sysml_parser=True)
    monkeypatch.setattr(PlatformSettings, "load", classmethod(lambda cls: settings))
    calls = []
    state = SimpleNamespace(final=10, corrections=False, corrected=False)

    class FakeReasoner:
        def __init__(self, settings, stage):
            self.settings, self.stage, self.calls, self.spent = settings, stage, 0, 0

        def ask(self, prompt, context, schema, packet, input_tables=None):
            self.calls += 1
            rendered = packet.render(input_tables)
            calls.append((schema, context, rendered))
            assert "requirements.txt" in rendered and "physics.txt" in rendered
            if schema is Understanding:
                corrected = "Correct this brief" in context
                state.corrected = corrected or state.corrected
                return Understanding(title="Accumulator", narrative="Revised engineering model" if corrected else "Engineering model",
                    simulation=Simulation(stop_time=10, intervals=10),
                    checks=[Check(name="Final accumulated value", expression="x", kind="final", expected=10, source="requirements.txt")])
            if schema is Review:
                return Review(passed=True, issues=[])
            if schema is SysMLDraft:
                if state.corrections and not state.corrected:
                    return SysMLDraft(code="", corrections=["Use the initial value from physics.txt"])
                return SysMLDraft(code="package Accumulator { part def System; part system : System; }")
            if schema is ModelicaDraft:
                return ModelicaDraft(model_name="Accumulator", code="model Accumulator Real x(start=0,fixed=true); equation der(x)=1; end Accumulator;")
            raise AssertionError(schema)

    def compile_mock(*args, **kwargs):
        kwargs["result_csv_path"].write_text("time,x\n" + "\n".join(f"{i},{state.final*i/10}" for i in range(11)))
        return CompileResult(execution_id="test", status=CompileStatus.PASSED, backend="test-double",
                             backend_version="0", duration_seconds=0)

    monkeypatch.setattr(pipeline, "Reasoner", FakeReasoner)
    monkeypatch.setattr(pipeline, "validate_files_with_real_parser", lambda files, timeout: [])
    monkeypatch.setattr(pipeline, "compile_files", compile_mock)
    return SimpleNamespace(docs=docs, root=settings.projects_root, calls=calls, state=state)


def test_three_stages_receive_complete_original_context_and_only_two_model_files(engine):
    result = pipeline.run_full_pipeline("generic", docs_dir=engine.docs, projects_root=engine.root)
    assert [stage.status for stage in result] == ["READY"] * 3
    project = engine.root / "generic"
    assert len(list(project.rglob("*.sysml"))) == 1
    assert len(list(project.rglob("*.mo"))) == 1
    assert not (project / "checkpoints.sqlite").exists()
    modelica_context = next(context for schema, context, _ in engine.calls if schema is ModelicaDraft)
    assert "Engineering model" in modelica_context and "package Accumulator" in modelica_context


def test_unchanged_inputs_skip_but_changed_document_regenerates(engine):
    pipeline.run_full_pipeline("generic", docs_dir=engine.docs, projects_root=engine.root)
    engine.calls.clear()
    skipped = pipeline.run_full_pipeline("generic", docs_dir=engine.docs, projects_root=engine.root)
    assert all(stage.details.get("skipped") for stage in skipped)
    assert not engine.calls
    (engine.docs / "physics.txt").write_text("Updated source evidence")
    pipeline.run_full_pipeline("generic", docs_dir=engine.docs, projects_root=engine.root)
    assert engine.calls


def test_missing_model_is_regenerated_and_modified_upstream_requires_validation(engine):
    pipeline.run_full_pipeline("generic", docs_dir=engine.docs, projects_root=engine.root)
    project = engine.root / "generic"
    (project / "Model.mo").unlink()
    assert pipeline.execute_stage_3("generic", projects_root=engine.root).status == "READY"
    (project / "Model.sysml").write_text("unvalidated manual edit")
    with pytest.raises(ValueError, match="modified"):
        pipeline.execute_stage_3("generic", projects_root=engine.root)


def test_later_stage_can_correct_the_understanding(engine):
    engine.state.corrections = True
    result = pipeline.run_full_pipeline("generic", docs_dir=engine.docs, projects_root=engine.root)
    assert all(stage.status == "READY" for stage in result)
    assert engine.state.corrected
    assert "Revised engineering model" in (engine.root / "generic" / "understanding.md").read_text()
    modelica_context = next(context for schema, context, _ in engine.calls if schema is ModelicaDraft)
    assert "Revised engineering model" in modelica_context


def test_compile_success_with_wrong_results_is_failed(engine):
    engine.state.final = 999
    result = pipeline.run_full_pipeline("generic", docs_dir=engine.docs, projects_root=engine.root)
    assert result[-1].status == "FAILED"
    assert any("Acceptance checks failed" in issue for issue in result[-1].details["issues"])


def test_source_changes_make_downstream_commands_refuse_stale_context(engine):
    pipeline.run_full_pipeline("generic", docs_dir=engine.docs, projects_root=engine.root)
    (engine.docs / "physics.txt").write_text("Changed source")
    with pytest.raises(ValueError, match="stale"):
        pipeline.execute_stage_3("generic", projects_root=engine.root)


def test_failed_rerun_cannot_leave_a_previous_passing_report(engine, monkeypatch):
    import json
    pipeline.run_full_pipeline("generic", docs_dir=engine.docs, projects_root=engine.root)
    def unavailable(*args, **kwargs):
        raise RuntimeError("API unavailable")
    monkeypatch.setattr(pipeline, "Reasoner", unavailable)
    with pytest.raises(RuntimeError, match="API unavailable"):
        pipeline.execute_stage_1("generic", projects_root=engine.root, force=True)
    report = json.loads((engine.root / "generic" / "report.json").read_text())
    assert report["passed"] is False
    assert report["status"] == "STALE"


def test_project_cannot_escape_workspace(engine):
    with pytest.raises(ValueError, match="within"):
        pipeline.workspace(engine.root).project_dir("../outside")


def test_cli_sources_is_offline_and_missing_project_is_clean(tmp_path, capsys):
    path = tmp_path / "problem.txt"
    path.write_text("A simple physical problem")
    assert main(["sources", "--docs", str(path)]) == 0
    assert "A simple physical problem" in capsys.readouterr().out


def test_actual_client_fails_cleanly_without_key(tmp_path, monkeypatch):
    from simulation_platform.reasoning import Reasoner, UNDERSTAND
    from simulation_platform.sources import Packet, Source
    settings = replace(PlatformSettings.load(), openai_api_key=None)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        Reasoner(settings, 1).ask(UNDERSTAND, "problem", Understanding, Packet([Source("problem.txt", "text")]))
