"""Core data structures for a single layered GRC cell.

The model is deliberately small and dependency-free. Records are stored in one
cell and grouped by layer; relationships connect records without splitting the
cell into separate GRC cells.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

GRC_LAYER_NAMES = (
    "identity_scope",
    "governance_obligations",
    "risk_controls",
    "evidence_assurance",
    "work_decisions",
    "history_provenance",
)


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


@dataclass
class GRCRecord:
    """A versioned GRC item held within a cell layer."""

    record_id: str
    record_type: str
    layer: str
    title: str
    data: dict[str, Any] = field(default_factory=dict)
    version: int = 1
    status: str = "active"

    def __post_init__(self) -> None:
        if not self.record_id.strip():
            raise ValueError("record_id must not be empty")
        if not self.record_type.strip():
            raise ValueError("record_type must not be empty")
        if self.layer not in GRC_LAYER_NAMES:
            raise ValueError(f"Unknown GRC layer: {self.layer}")
        if not self.title.strip():
            raise ValueError("title must not be empty")
        if self.version < 1:
            raise ValueError("version must be at least 1")


@dataclass(frozen=True)
class GRCRelationship:
    """An explicit, typed link between two records in the same cell."""

    relationship_id: str
    source_record_id: str
    target_record_id: str
    relationship_type: str
    data: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not all((self.relationship_id, self.source_record_id,
                    self.target_record_id, self.relationship_type)):
            raise ValueError("relationship identifiers and type must not be empty")
        if self.source_record_id == self.target_record_id:
            raise ValueError("self relationships are not supported")


@dataclass(frozen=True)
class GRCSignal:
    """An immutable event moving through the cell's signal network."""

    signal_type: str
    source: str
    payload: dict[str, Any] = field(default_factory=dict)
    signal_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)
    parent_signal_id: str | None = None

    def __post_init__(self) -> None:
        if not self.signal_type.strip() or not self.source.strip():
            raise ValueError("signal_type and source must not be empty")


@dataclass
class GRCCell:
    """One organizational GRC cell containing layered records and links."""

    cell_id: str
    name: str
    scope: str
    records: dict[str, GRCRecord] = field(default_factory=dict)
    relationships: dict[str, GRCRelationship] = field(default_factory=dict)
    signal_history: list[GRCSignal] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.cell_id.strip() or not self.name.strip() or not self.scope.strip():
            raise ValueError("cell_id, name, and scope must not be empty")

    def add_record(self, record: GRCRecord) -> None:
        if record.record_id in self.records:
            raise ValueError(f"Duplicate record ID: {record.record_id}")
        self.records[record.record_id] = record

    def link(self, relationship: GRCRelationship) -> None:
        if relationship.relationship_id in self.relationships:
            raise ValueError(f"Duplicate relationship ID: {relationship.relationship_id}")
        if relationship.source_record_id not in self.records:
            raise ValueError(f"Unknown source record: {relationship.source_record_id}")
        if relationship.target_record_id not in self.records:
            raise ValueError(f"Unknown target record: {relationship.target_record_id}")
        self.relationships[relationship.relationship_id] = relationship

    def related_records(self, record_id: str, relationship_types: set[str] | None = None) -> list[GRCRecord]:
        """Return directly connected records, following links in either direction."""
        if record_id not in self.records:
            raise KeyError(f"Unknown record: {record_id}")
        matches: set[str] = set()
        for link in self.relationships.values():
            if relationship_types is not None and link.relationship_type not in relationship_types:
                continue
            if link.source_record_id == record_id:
                matches.add(link.target_record_id)
            elif link.target_record_id == record_id:
                matches.add(link.source_record_id)
        return [self.records[item] for item in sorted(matches)]
