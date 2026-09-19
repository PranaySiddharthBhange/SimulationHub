"""Shared fixture builder: a minimal but realistic upstream project tree
(Document Agent's `source/original/`, SysML Agent's `sysml/input/` +
`sysml/traceability/` + `sysml/generated/`), used by every test that
exercises `build_upstream_bundle` or the full workflow.
"""

from __future__ import annotations

import json
from pathlib import Path

_LEGACY_TANK_MO = """\
within SyntheticTankDemo;
model TankDemo_Rev12
  parameter Real h1High(unit="m") = 0.78;
end TankDemo_Rev12;
"""


def seed_upstream_project(tmp_path: Path, project_id: str = "tank_001", include_legacy: bool = True) -> tuple[Path, Path]:
    """Returns `(document_agent_project_dir, sysml_project_dir)`."""

    document_agent_project_dir = tmp_path / "document_agent_projects" / project_id
    sysml_project_dir = tmp_path / "sysml_projects" / project_id

    sysml_input_dir = sysml_project_dir / "sysml" / "input"
    sysml_input_dir.mkdir(parents=True)
    (sysml_input_dir / "generation_contract.json").write_text(
        json.dumps(
            {
                "project_id": project_id,
                "version": {"knowledge_version": "v0008"},
                "entities": [
                    {"id": "ENT-001", "name": "TankDemo", "type": "Tank", "status": "EXPLICIT", "evidence": ["EV-1"]}
                ],
                "relationships": [],
                "requirements": [
                    {
                        "id": "REQ-001", "subject": "TankDemo", "property": "h1High", "operator": "<=",
                        "value": None, "min": None, "max": 0.78, "unit": "m",
                        "status": "CONFIRMED", "evidence": ["EV-1"],
                    }
                ],
                "behaviors": [], "constraints": [], "interfaces": [],
                "evidence": [{"evidence_id": "EV-1", "document_id": "doc_001", "location": {"page": 1}}],
            }
        ),
        encoding="utf-8",
    )

    sysml_trace_dir = sysml_project_dir / "sysml" / "traceability"
    sysml_trace_dir.mkdir(parents=True)
    (sysml_trace_dir / "sysml_traceability.json").write_text(
        json.dumps(
            {
                "sysml_version": "v0004",
                "entries": [
                    {"engineering_id": "ENT-001", "sysml_element": "TankDemo", "file": "Architecture.sysml", "evidence": ["EV-1"]},
                    {"engineering_id": "REQ-001", "sysml_element": "TankDemoRequirement", "file": "Requirements.sysml", "evidence": ["EV-1"]},
                ],
            }
        ),
        encoding="utf-8",
    )

    sysml_generated_dir = sysml_project_dir / "sysml" / "generated"
    sysml_generated_dir.mkdir(parents=True)
    (sysml_generated_dir / "Architecture.sysml").write_text(
        "package Architecture {\n"
        "    part def TankDemo;\n"
        "    part tankDemo : TankDemo;\n"
        "}\n",
        encoding="utf-8",
    )
    (sysml_generated_dir / "Requirements.sysml").write_text(
        "package Requirements {\n"
        "    requirement def TankDemoRequirement {\n"
        "        doc /* TankDemo.h1High <= 0.78 m */\n"
        "        attribute h1High : Real;\n"
        "    }\n"
        "}\n",
        encoding="utf-8",
    )

    if include_legacy:
        legacy_dir = document_agent_project_dir / "source" / "original" / "06_legacy_code"
        legacy_dir.mkdir(parents=True)
        (legacy_dir / "07_legacy_tank_demo.mo").write_text(_LEGACY_TANK_MO, encoding="utf-8")
    else:
        document_agent_project_dir.mkdir(parents=True)

    return document_agent_project_dir, sysml_project_dir
