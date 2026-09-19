"""Project manifest. Mirrors `Document Agent.md`, Section 6 (Project Creation)."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class ProjectStatus(str, Enum):
    CREATED = "CREATED"
    INGESTING = "INGESTING"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    READY = "READY"
    FAILED = "FAILED"


class ProjectManifest(BaseModel):
    project_id: str
    name: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_root: str
    status: ProjectStatus = ProjectStatus.CREATED
    knowledge_version: str = "v0000"
