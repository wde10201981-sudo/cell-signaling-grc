"""Signal routing and a first deterministic change-propagation handler."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterable

from .models import GRCCell, GRCSignal

SignalHandler = Callable[[GRCCell, GRCSignal], Iterable[GRCSignal]]


class SignalBus:
    """Route signals synchronously and record each event in the cell.

    Handlers return follow-up signals instead of directly mutating unrelated
    records. The event limit protects the prototype against accidental loops.
    """

    def __init__(self, *, max_events_per_publish: int = 100) -> None:
        if max_events_per_publish < 1:
            raise ValueError("max_events_per_publish must be at least 1")
        self.max_events_per_publish = max_events_per_publish
        self._handlers: dict[str, list[SignalHandler]] = {}

    def subscribe(self, signal_type: str, handler: SignalHandler) -> None:
        if not signal_type.strip():
            raise ValueError("signal_type must not be empty")
        self._handlers.setdefault(signal_type, []).append(handler)

    def publish(self, cell: GRCCell, signal: GRCSignal) -> list[GRCSignal]:
        """Record and route a signal, including any follow-up signals."""
        queue = deque([signal])
        processed: list[GRCSignal] = []
        seen_ids = {item.signal_id for item in cell.signal_history}

        while queue:
            if len(processed) >= self.max_events_per_publish:
                raise RuntimeError("Signal processing limit reached; possible event loop")
            current = queue.popleft()
            if current.signal_id in seen_ids:
                raise ValueError(f"Duplicate signal ID: {current.signal_id}")
            seen_ids.add(current.signal_id)
            cell.signal_history.append(current)
            processed.append(current)
            for handler in self._handlers.get(current.signal_type, ()):
                follow_ups = handler(cell, current)
                if follow_ups:
                    queue.extend(follow_ups)

        return processed


def requirement_change_handler(cell: GRCCell, signal: GRCSignal) -> Iterable[GRCSignal]:
    """Emit an impact summary for records linked to a changed requirement.

    Expected payload: {"record_id": "REQ-...", "change_summary": "..."}.
    Relationship direction is not significant for discovery. This handler
    identifies candidates only; it does not assert compliance or change records.
    """
    record_id = signal.payload.get("record_id")
    if not isinstance(record_id, str) or record_id not in cell.records:
        raise ValueError("requirement-change signal must reference a known record")
    requirement = cell.records[record_id]
    if requirement.record_type != "requirement":
        raise ValueError(f"Record {record_id} is not a requirement")

    impacted = cell.related_records(record_id)
    impact_payload = {
        "requirement_id": record_id,
        "change_summary": signal.payload.get("change_summary", ""),
        "candidate_impact_ids": [item.record_id for item in impacted],
        "requires_review": True,
    }
    return [GRCSignal(
        signal_type="requirement.impact_assessed",
        source="core.requirement_change_handler",
        payload=impact_payload,
        parent_signal_id=signal.signal_id,
    )]
