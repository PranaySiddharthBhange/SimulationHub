from pathlib import Path

import pytest
from pydantic import ValidationError

from simulation_platform.contracts import ModelicaDraft, ModelicaFile
from simulation_platform.skills.modelica_catalog import modelica_catalog_block
from simulation_platform.tools import modelica_validator


def _file(filename: str, role: str, class_name: str) -> ModelicaFile:
    return ModelicaFile(filename=filename, role=role, code=f"model {class_name}\nequation\nend {class_name};")


def test_modelica_bundle_requires_unique_files_and_one_system() -> None:
    valid = ModelicaDraft(
        entry_class="System",
        files=[_file("Tank1.mo", "component", "Tank1"), _file("System.mo", "system", "System")],
    )
    assert [file.filename for file in valid.files] == ["Tank1.mo", "System.mo"]

    with pytest.raises(ValidationError, match="exactly one system"):
        ModelicaDraft(
            entry_class="System",
            files=[_file("Tank1.mo", "component", "Tank1"), _file("System.mo", "component", "System")],
        )


def test_catalog_selects_verified_tank_and_magnetic_components() -> None:
    tank = modelica_catalog_block(["fluid_level_and_flow"])
    magnetic = modelica_catalog_block(["magnetic_circuit"])
    assert "Modelica.Blocks.Continuous.Integrator" in tank
    assert "Tank1.mo" in tank and "Tank2.mo" in tank
    assert "Modelica.Magnetic.FluxTubes.Basic.ConstantReluctance" in magnetic


def test_compiler_preserves_declared_bundle_load_order(monkeypatch, tmp_path: Path) -> None:
    scripts: list[str] = []

    def fake_run(_omc_path, script_name, workdir, _timeout):
        scripts.append((workdir / script_name).read_text(encoding="utf-8"))
        if script_name == "simulate.mos":
            (workdir / "System_res.csv").write_text("time,x\n0,0\n1,1\n", encoding="utf-8")
            return "The simulation finished successfully", False
        return "", False

    monkeypatch.setattr(modelica_validator, "find_omc_executable", lambda: Path("omc"))
    monkeypatch.setattr(modelica_validator, "_run_omc_script", fake_run)
    files = {
        "Tank1.mo": "model Tank1\nequation\nend Tank1;",
        "Tank2.mo": "model Tank2\nequation\nend Tank2;",
        "System.mo": "model System\nequation\nend System;",
    }
    result = modelica_validator.compile_files("order", files, "System", stop_time=1, result_csv_path=tmp_path / "out.csv")
    assert result.status.value == "PASSED"
    assert scripts[0].index('loadFile("Tank1.mo")') < scripts[0].index('loadFile("System.mo")')
