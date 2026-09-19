from pathlib import Path

import pytest

from benchmarks.run import run_reference
from simulation_platform.compiler.openmodelica_client import CompilerUnavailable, compile_files, find_omc_executable
from simulation_platform.compiler.sysml_parser import find_kernel_dir, validate_files_with_real_parser
from simulation_platform.verification import read_trajectory, sample


def has_omc():
    try:
        return find_omc_executable().exists()
    except CompilerUnavailable:
        return False


@pytest.mark.skipif(not has_omc(), reason="OpenModelica is not installed")
def test_real_compiler_rejects_missing_equations_and_preserves_log(tmp_path):
    code = "model Underdetermined Real x; Real y; equation x+y=1; end Underdetermined;"
    result = compile_files("bad", {"Underdetermined.mo": code}, "Underdetermined", log_path=tmp_path / "compiler.log")
    assert result.status.value == "FAILED"
    assert result.errors
    assert (tmp_path / "compiler.log").exists()


@pytest.mark.skipif(not has_omc(), reason="OpenModelica is not installed")
@pytest.mark.parametrize("name", ["tank", "iaq", "magnetic"])
def test_reference_models_match_independent_released_benchmarks(name, tmp_path):
    report = run_reference(name, tmp_path / name)
    assert report["passed"], report
    assert report["agent_generation_tested"] is False


@pytest.mark.skipif(find_kernel_dir() is None, reason="SysML parser is not installed")
def test_real_sysml_parser_checks_valid_and_invalid_models():
    assert validate_files_with_real_parser({"Model.sysml": "package A { part def Tank; part tank : Tank; }"}, 90) == []
    issues = validate_files_with_real_parser({"Broken.sysml": "package Broken { part def ;;; }"}, 90)
    assert issues and all(issue.file == "Broken.sysml" for issue in issues)


@pytest.mark.skipif(not has_omc(), reason="OpenModelica is not installed")
def test_tank_stop_freezes_remaining_delay_and_resumes_without_restart(tmp_path):
    root = Path(__file__).resolve().parents[1]
    code = (root / "benchmarks/reference_models/TankBenchmark.mo").read_text()
    code += "\nmodel PauseTest extends TankBenchmark(startTimes={20,184},stopTimes={174},shutTimes={210}); end PauseTest;"
    output = tmp_path / "pause.csv"
    result = compile_files("pause", {"PauseTest.mo": code}, "PauseTest", stop_time=205,
                           number_of_intervals=205, tolerance=1e-8, result_csv_path=output)
    assert result.status.value == "PASSED", result.errors
    rows = read_trajectory(output)
    assert sample(rows, 180)["wait_remaining_s"] == pytest.approx(6, abs=1e-5)
    assert sample(rows, 185)["wait_remaining_s"] == pytest.approx(5, abs=1e-5)
    assert sample(rows, 191)["valve2_open"] == 1


@pytest.mark.skipif(not has_omc(), reason="OpenModelica is not installed")
def test_tank_shut_wins_simultaneous_commands_and_ignores_stop_start_until_empty(tmp_path):
    root = Path(__file__).resolve().parents[1]
    code = (root / "benchmarks/reference_models/TankBenchmark.mo").read_text()
    code += "\nmodel PriorityTest extends TankBenchmark(startTimes={20,40,45},stopTimes={40,46},shutTimes={40}); end PriorityTest;"
    output = tmp_path / "priority.csv"
    result = compile_files("priority", {"PriorityTest.mo": code}, "PriorityTest", stop_time=70,
                           number_of_intervals=70, tolerance=1e-8, result_csv_path=output)
    assert result.status.value == "PASSED", result.errors
    rows = read_trajectory(output)
    assert sample(rows, 41)["phase"] == 7
    assert sample(rows, 47)["phase"] == 7
    assert sample(rows, 47)["valve1_open"] == 0
    assert rows[-1]["phase"] == 0
