"""Adapter: Document Agent's `semantic_model.json` -> SysML Generation Contract.

Mirrors `SysML V2 Agent.md`, Section 5 ("Create the Generation Contract").
Reads the Document Agent's published knowledge as plain JSON — no import
of the `engineering_agent` package, so the two agents stay decoupled and
only share a JSON shape, exactly like two real services would.
"""

from __future__ import annotations

import json
from pathlib import Path

from simulation_platform.schemas import (
    BehaviorItem,
    ConstraintItem,
    ControlLawItem,
    EntityItem,
    EvidenceRecord,
    InterfaceItem,
    RelationshipItem,
    RequirementItem,
    ScheduledCommandItem,
    SysMLGenerationContract,
    VersionRef,
)


def contract_from_semantic_model(document_agent_project_dir: Path) -> SysMLGenerationContract:
    model_path = document_agent_project_dir / "workspace" / "extracted" / "project_knowledge.json"
    model = json.loads(model_path.read_text(encoding="utf-8"))

    return SysMLGenerationContract(
        project_id=model["project_id"],
        version=VersionRef(knowledge_version=model["model_version"]),
        entities=[
            EntityItem(id=e["entity_id"], name=e["name"], type=e["type"], status=e["status"], evidence=e["evidence"])
            for e in model.get("entities", [])
        ],
        relationships=[
            RelationshipItem(source=r["source"], target=r["target"], type=r["type"], evidence=r["evidence"])
            for r in model.get("relationships", [])
        ],
        requirements=[
            RequirementItem(
                id=r["requirement_id"], subject=r["subject"], property=r["property"], operator=r["operator"],
                value=r.get("value"), min=r.get("min"), max=r.get("max"), unit=r.get("unit"), status=r["status"],
                evidence=r["evidence"],
            )
            for r in model.get("requirements", [])
        ],
        behaviors=[
            BehaviorItem(
                id=b["behavior_id"], trigger_property=b["trigger_property"], trigger_operator=b["trigger_operator"],
                trigger_value=b["trigger_value"], trigger_unit=b.get("trigger_unit"), action_type=b["action_type"],
                action_target=b["action_target"], status=b["status"], evidence=b["evidence"],
            )
            for b in model.get("behaviors", [])
        ],
        control_laws=[
            ControlLawItem(
                id=cl["control_law_id"], law_type=cl["law_type"], controlled_property=cl["controlled_property"],
                input_property=cl["input_property"], gain_p=cl.get("gain_p"), gain_i=cl.get("gain_i"),
                gain_d=cl.get("gain_d"), setpoint=cl.get("setpoint"), setpoint_unit=cl.get("setpoint_unit"),
                status=cl["status"], evidence=cl["evidence"],
            )
            for cl in model.get("control_laws", [])
        ],
        scheduled_commands=[
            ScheduledCommandItem(
                id=sc["command_id"], command_name=sc["command_name"], time_value=sc["time_value"],
                time_unit=sc.get("time_unit"), expected_response=sc.get("expected_response"),
                status=sc["status"], evidence=sc["evidence"],
            )
            for sc in model.get("scheduled_commands", [])
        ],
        constraints=[
            ConstraintItem(
                id=c["constraint_id"], subject=c["subject"], property=c["property"], min=c.get("min"),
                max=c.get("max"), unit=c.get("unit"), evidence=c["evidence"],
            )
            for c in model.get("constraints", [])
        ],
        interfaces=[],  # Document Agent does not yet extract interfaces as a distinct fact type
        evidence=[
            EvidenceRecord(evidence_id=e["evidence_id"], document_id=e["document_id"], quote=e.get("quote"))
            for e in model.get("evidence", [])
        ],
    )
