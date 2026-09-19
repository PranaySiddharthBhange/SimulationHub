"""ONE flat schema package for the whole platform -- consolidated from
three independently-invented schema packages (one per former agent).
`Comparator`/`FactStatus`/`VersionRef`/`ValidationStatus`/`OpenQuestion`
were each duplicated across two or three of the originals; they now have
exactly one definition, in `common.py` (see that module's docstring for
which shape won when they weren't byte-identical).

Filenames that collided across packages (`generation_contract.py`,
`generation_plan.py`, `manifest.py`, `mapping.py`, `traceability.py`,
`validation.py`) are prefixed `sysml_`/`modelica_` to tell them apart;
everything else keeps its original name.
"""

from __future__ import annotations

from .behavior import Behavior
from .control_law import ControlLaw, ControlLawType
from .scheduled_command import ScheduledCommand
from .common import (
    Comparator,
    EvidenceRef,
    FactStatus,
    OpenQuestion,
    SourceLocation,
    ValidationStatus,
    VersionRef,
)
from .compiler_result import CompileError, CompileResult, CompileStatus, CompileWarning, ErrorCategory
from .constraint import Constraint
from .decision import ClarificationRequest, Decision
from .document import DocumentRecord, DocumentRole, InformationType, ParseStatus, SourceManifest
from .entity import Entity
from .evidence import Evidence, EvidenceType
from .legacy import LegacyClass, LegacyComparison, LegacyModel, LegacyParameter, LegacyRecommendation, LegacyVariable
from .modelica_generation_contract import ModelicaGenerationContract
from .modelica_generation_plan import ModelicaGenerationPlan
from .modelica_manifest import ModelicaManifest
from .modelica_mapping import ModelicaMapping, ModelicaMappingType
from .modelica_traceability import ModelicaTraceability, ModelicaTraceEntity, ModelicaTraceRequirement
from .modelica_validation import ModelicaValidationIssue, ModelicaValidationResult, ValidationLayer
from .observation import Observation, ObservationType
from .project import ProjectManifest, ProjectStatus
from .relationship import Relationship
from .requirement import Requirement
from .sysml_generation_contract import (
    BehaviorItem,
    ConstraintItem,
    ControlLawItem,
    ScheduledCommandItem,
    EntityItem,
    EvidenceRecord,
    InterfaceItem,
    RelationshipItem,
    RequirementItem,
    SysMLGenerationContract,
)
from .sysml_generation_plan import SysMLGenerationPlan
from .sysml_manifest import SysMLManifest
from .sysml_mapping import SysMLConstruct, SysMLElementMapping
from .sysml_semantic import (
    SysMLBehavior,
    SysMLConnection,
    SysMLConstraint,
    SysMLInterface,
    SysMLPart,
    SysMLRequirement,
    SysMLSemanticModel,
)
from .sysml_traceability import SysMLTraceability, SysMLTraceEntry
from .sysml_validation import RequirementCoverage, SemanticIssue, StructuralIssue, SyntaxIssue, SysMLValidationResult, TraceabilityIssue
from .resolved_system_model import ResolvedParameter, ResolvedSystemModel
from .state_machine import StateMachine, StateTransition
from .system_model import SemanticModel
from .uncertainty import Ambiguity, Assumption, Conflict, ConflictStatus, ImpactLevel, Unknown

__all__ = [
    "Behavior",
    "ControlLaw",
    "ControlLawType",
    "ScheduledCommand",
    "Comparator",
    "EvidenceRef",
    "FactStatus",
    "OpenQuestion",
    "SourceLocation",
    "ValidationStatus",
    "VersionRef",
    "CompileError",
    "CompileResult",
    "CompileStatus",
    "CompileWarning",
    "ErrorCategory",
    "Constraint",
    "ClarificationRequest",
    "Decision",
    "DocumentRecord",
    "DocumentRole",
    "InformationType",
    "ParseStatus",
    "SourceManifest",
    "Entity",
    "Evidence",
    "EvidenceType",
    "LegacyClass",
    "LegacyComparison",
    "LegacyModel",
    "LegacyParameter",
    "LegacyRecommendation",
    "LegacyVariable",
    "ModelicaGenerationContract",
    "ModelicaGenerationPlan",
    "ModelicaManifest",
    "ModelicaMapping",
    "ModelicaMappingType",
    "ModelicaTraceability",
    "ModelicaTraceEntity",
    "ModelicaTraceRequirement",
    "ModelicaValidationIssue",
    "ModelicaValidationResult",
    "ValidationLayer",
    "Observation",
    "ObservationType",
    "ProjectManifest",
    "ProjectStatus",
    "Relationship",
    "Requirement",
    "BehaviorItem",
    "ControlLawItem",
    "ScheduledCommandItem",
    "ConstraintItem",
    "EntityItem",
    "EvidenceRecord",
    "InterfaceItem",
    "RelationshipItem",
    "RequirementItem",
    "SysMLGenerationContract",
    "SysMLGenerationPlan",
    "SysMLManifest",
    "SysMLConstruct",
    "SysMLElementMapping",
    "SysMLBehavior",
    "SysMLConnection",
    "SysMLConstraint",
    "SysMLInterface",
    "SysMLPart",
    "SysMLRequirement",
    "SysMLSemanticModel",
    "SysMLTraceability",
    "SysMLTraceEntry",
    "RequirementCoverage",
    "SemanticIssue",
    "StructuralIssue",
    "SyntaxIssue",
    "SysMLValidationResult",
    "TraceabilityIssue",
    "ResolvedParameter",
    "ResolvedSystemModel",
    "StateMachine",
    "StateTransition",
    "SemanticModel",
    "Ambiguity",
    "Assumption",
    "Conflict",
    "ConflictStatus",
    "ImpactLevel",
    "Unknown",
]
