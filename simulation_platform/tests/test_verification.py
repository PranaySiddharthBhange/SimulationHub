import pytest

from simulation_platform.contracts import Check, ReferenceColumn, Simulation
from simulation_platform.verification import check_results, compare_reference, expression_value, export_uniform_results, read_trajectory, sample


def test_expressions_check_actual_physics_without_running_python():
    row = {"a": 4, "b": 5, "tank.level": 0.8}
    assert expression_value('a+b == 9 and value("tank.level") <= 0.8', row) == 1
    assert expression_value("a == 0 or 1/a > 0", {"a": 0}) == 1
    with pytest.raises((ValueError, KeyError)):
        expression_value('__import__("os").system("echo forbidden")', row)


def test_post_event_value_is_used_at_duplicate_time():
    rows = [{"time": 0., "x": 0.}, {"time": 1., "x": 0.}, {"time": 1., "x": 1.}, {"time": 2., "x": 2.}]
    assert sample(rows, 1)["x"] == 1
    assert sample(rows, 1.5)["x"] == 1.5
    with pytest.raises(ValueError, match="outside"):
        sample(rows, 3)


def test_solver_event_roundoff_does_not_compare_previous_occupancy(tmp_path):
    rows = [{"time": 0., "x": 0.}, {"time": 1., "x": 0.},
            {"time": 1.00000009, "x": 0.}, {"time": 1.00000009, "x": 2.}, {"time": 2., "x": 2.}]
    assert sample(rows, 1)["x"] == 2
    path = tmp_path / "result.csv"
    path.write_text("time,x\n0,0\n1,0\n1.00000009,0\n1.00000009,2\n2,2\n")
    assert export_uniform_results(path, Simulation(stop_time=2, intervals=2)) == 3
    assert read_trajectory(path)[1] == {"time": 1., "x": 2.}


def test_compiled_but_wrong_results_cannot_pass(tmp_path):
    csv = tmp_path / "result.csv"
    csv.write_text("time,x\n0,0\n10,999\n")
    report = check_results(csv, [Check(name="Expected output", expression="x", kind="final", expected=10, source="URS")],
                           Simulation(stop_time=10))
    assert not report["passed"]
    assert report["checks"][0]["max_error"] == 989


def test_at_time_continuous_check_does_not_use_previous_logging_sample(tmp_path):
    path = tmp_path / "result.csv"
    path.write_text("time,x\n0,0\n10,10\n")
    check = Check(name="Midpoint", expression="x", kind="at", at_time=5.5, expected=5.5, source="URS")
    assert check_results(path, [check], Simulation(stop_time=10))["passed"]


@pytest.mark.parametrize("text", ["time,x\n0,0\n5,10\n", "time,x\n0,0\n10,nan\n", "time,x\n10,10\n0,0\n"])
def test_partial_nonfinite_and_backwards_simulations_fail(tmp_path, text):
    path = tmp_path / "result.csv"
    path.write_text(text)
    report = check_results(path, [Check(name="Final", expression="x", kind="final", expected=10, source="URS")], Simulation(stop_time=10))
    assert not report["passed"]


def test_no_checks_and_missing_output_are_failures(tmp_path):
    path = tmp_path / "result.csv"
    path.write_text("time,x\n0,0\n10,10\n")
    assert not check_results(path, [], Simulation(stop_time=10))["passed"]
    check = Check(name="Missing", expression="missing", kind="final", expected=0, source="URS")
    assert not check_results(path, [check], Simulation(stop_time=10))["passed"]


def test_reference_comparison_requires_full_time_coverage(tmp_path):
    actual, reference = tmp_path / "actual.csv", tmp_path / "ref.csv"
    actual.write_text("time,x\n0,0\n5,5\n")
    reference.write_text("time_s,y\n0,0\n10,10\n")
    mapping = ReferenceColumn(path="ref.csv", time_column="time_s", reference_column="y", model_variable="x",
                              absolute_tolerance=0.01, reason="test")
    assert not compare_reference(actual, tmp_path, mapping)["passed"]


def test_event_tolerance_uses_source_defined_window(tmp_path):
    actual, reference = tmp_path / "actual.csv", tmp_path / "ref.csv"
    actual.write_text("time,x\n0,0\n1,0\n2,1\n3,1\n")
    reference.write_text("t,y\n0,0\n1,1\n3,1\n")
    mapping = ReferenceColumn(path="ref.csv", time_column="t", reference_column="y", model_variable="x",
                              absolute_tolerance=0, interpolation="previous", reason="one-second logger")
    assert not compare_reference(actual, tmp_path, mapping)["passed"]
    mapping.time_tolerance = 1
    assert compare_reference(actual, tmp_path, mapping)["passed"]
