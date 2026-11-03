"""Runnable synthetic demonstration of the cell's first signal pathway."""

from .engine import SignalBus, requirement_change_handler
from .models import GRCCell, GRCRecord, GRCRelationship, GRCSignal


def build_demo_cell() -> GRCCell:
    cell = GRCCell(
        cell_id="CELL-DEMO-001",
        name="Example Organization GRC Cell",
        scope="Synthetic demonstration only",
    )
    cell.add_record(GRCRecord(
        record_id="REQ-001", record_type="requirement",
        layer="governance_obligations", title="Access review requirement",
        data={"text": "Privileged access must be reviewed periodically."},
    ))
    cell.add_record(GRCRecord(
        record_id="CTRL-001", record_type="control",
        layer="risk_controls", title="Privileged access review",
        data={"owner": "synthetic-owner"},
    ))
    cell.add_record(GRCRecord(
        record_id="EVD-001", record_type="evidence",
        layer="evidence_assurance", title="Quarterly access review record",
        data={"freshness": "unknown"},
    ))
    cell.link(GRCRelationship(
        relationship_id="LINK-001", source_record_id="REQ-001",
        target_record_id="CTRL-001", relationship_type="implemented_by",
    ))
    cell.link(GRCRelationship(
        relationship_id="LINK-002", source_record_id="CTRL-001",
        target_record_id="EVD-001", relationship_type="supported_by",
    ))
    return cell


def main() -> None:
    cell = build_demo_cell()
    bus = SignalBus()
    bus.subscribe("requirement.changed", requirement_change_handler)
    events = bus.publish(cell, GRCSignal(
        signal_type="requirement.changed",
        source="demo.synthetic_input",
        payload={"record_id": "REQ-001", "change_summary": "Review frequency changed."},
    ))
    for event in events:
        print(f"{event.signal_type}: {event.payload}")


if __name__ == "__main__":
    main()
