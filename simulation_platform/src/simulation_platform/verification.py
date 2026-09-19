"""Independent numerical checks on actual trajectories, not compiler success."""

from __future__ import annotations

import ast
import bisect
import csv
import math
import operator
from pathlib import Path

from simulation_platform.contracts import Check, ReferenceColumn, Simulation

_BINARY = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
           ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod}
_COMPARE = {ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt,
            ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge}
_FUNCTIONS = {"abs": abs, "min": min, "max": max, "sqrt": math.sqrt}


def expression_value(expression: str, row: dict[str, float]) -> float:
    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float, bool)):
            return node.value
        if isinstance(node, ast.Name):
            return row[node.id]
        if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
            return _BINARY[type(node.op)](visit(node.left), visit(node.right))
        if isinstance(node, ast.UnaryOp):
            operand = visit(node.operand)
            if isinstance(node.op, ast.USub):
                return -operand
            if isinstance(node.op, ast.UAdd):
                return operand
            if isinstance(node.op, ast.Not):
                return not operand
        if isinstance(node, ast.Compare):
            left = visit(node.left)
            for op, right_node in zip(node.ops, node.comparators):
                if type(op) not in _COMPARE:
                    raise ValueError("Unsupported comparison")
                right = visit(right_node)
                if not _COMPARE[type(op)](left, right):
                    return False
                left = right
            return True
        if isinstance(node, ast.BoolOp):
            values = [bool(visit(value)) for value in node.values]
            return all(values) if isinstance(node.op, ast.And) else any(values)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
            if node.func.id == "value" and len(node.args) == 1 and isinstance(node.args[0], ast.Constant):
                return row[node.args[0].value]
            if node.func.id in _FUNCTIONS:
                return _FUNCTIONS[node.func.id](*(visit(arg) for arg in node.args))
        raise ValueError(f"Unsupported check expression: {expression}")

    value = float(visit(ast.parse(expression, mode="eval")))
    if not math.isfinite(value):
        raise ValueError("Non-finite check result")
    return value


def read_trajectory(path: Path, time_column: str = "time") -> list[dict[str, float]]:
    rows = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for source in csv.DictReader(handle):
            row = {}
            for key, value in source.items():
                try:
                    number = float(value)
                except (ValueError, TypeError):
                    continue
                if not math.isfinite(number):
                    raise ValueError(f"Non-finite simulation/reference value in {path.name}: {key}")
                row[key] = number
            if time_column not in row:
                raise ValueError(f"Missing numeric time column {time_column} in {path}")
            rows.append(row)
    if not rows or any(b[time_column] < a[time_column] for a, b in zip(rows, rows[1:])):
        raise ValueError(f"Empty or non-monotonic trajectory: {path}")
    return rows


def sample(rows: list[dict[str, float]], time: float, interpolation: str = "linear") -> dict[str, float]:
    times = [row["time"] for row in rows]
    if time < times[0] - 1e-8 or time > times[-1] + 1e-8:
        raise ValueError(f"Requested time {time} outside simulated range {times[0]}..{times[-1]}")
    index = bisect.bisect_right(times, time + 1e-10) - 1
    left = rows[max(index, 0)]
    if interpolation == "previous" or index >= len(rows) - 1 or abs(left["time"] - time) < 1e-9:
        return left
    right = rows[index + 1]
    fraction = (time - left["time"]) / (right["time"] - left["time"])
    return {key: value + fraction * (right[key] - value) for key, value in left.items() if key in right}


def check_results(path: Path, checks: list[Check], simulation: Simulation) -> dict:
    results = []
    try:
        rows = read_trajectory(path)
        if abs(rows[0]["time"] - simulation.start_time) > 1e-6 or abs(rows[-1]["time"] - simulation.stop_time) > 1e-6:
            raise ValueError("Simulation did not cover the complete requested time window")
        for check in checks:
            try:
                selected = rows if check.kind == "always" else [rows[-1]]
                if check.kind == "at":
                    if check.at_time is None:
                        raise ValueError("An at check requires at_time")
                    selected = [sample(rows, check.at_time, "previous")]
                errors = [abs(expression_value(check.expression, row) - check.expected) for row in selected]
                allowed = check.absolute_tolerance + check.relative_tolerance * abs(check.expected)
                results.append({"name": check.name, "passed": max(errors) <= allowed,
                                "max_error": max(errors), "tolerance": allowed, "source": check.source})
            except (KeyError, ValueError, TypeError, ArithmeticError, SyntaxError) as exc:
                results.append({"name": check.name, "passed": False, "error": str(exc)})
    except (OSError, ValueError) as exc:
        return {"passed": False, "checks": [], "error": str(exc)}
    return {"passed": bool(results) and all(result["passed"] for result in results), "checks": results}


def compare_reference(actual_path: Path, source_root: Path, mapping: ReferenceColumn) -> dict:
    try:
        reference_path = (source_root / mapping.path).resolve()
        if not reference_path.is_relative_to(source_root.resolve()):
            raise ValueError("Reference path escapes the source packet")
        expected = read_trajectory(reference_path, mapping.time_column)
        actual = read_trajectory(actual_path)
        errors = []
        for row in expected:
            measured = sample(actual, row[mapping.time_column], mapping.interpolation)[mapping.model_variable]
            target = row[mapping.reference_column]
            allowed = mapping.absolute_tolerance + mapping.relative_tolerance * abs(target)
            errors.append((abs(measured - target), allowed))
        return {"column": mapping.reference_column, "variable": mapping.model_variable,
                "passed": all(error <= allowed for error, allowed in errors), "samples": len(errors),
                "max_error": max(error for error, _ in errors), "reason": mapping.reason}
    except (OSError, ValueError, KeyError) as exc:
        return {"column": mapping.reference_column, "passed": False, "error": str(exc)}
