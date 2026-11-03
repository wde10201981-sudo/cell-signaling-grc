"""Tests for the isolated Cell Signaling GRC skeleton."""

import unittest

from cell_signaling.demo import build_demo_cell
from cell_signaling.engine import SignalBus, requirement_change_handler
from cell_signaling.models import GRCRecord, GRCRelationship, GRCSignal


class CellModelTests(unittest.TestCase):
    def test_records_are_layered_inside_one_cell(self):
        cell = build_demo_cell()
        self.assertEqual(len(cell.records), 3)
        self.assertEqual(cell.records["REQ-001"].layer, "governance_obligations")
        self.assertEqual(cell.records["CTRL-001"].layer, "risk_controls")

    def test_links_require_records_to_exist(self):
        cell = build_demo_cell()
        with self.assertRaisesRegex(ValueError, "Unknown target"):
            cell.link(GRCRelationship("BAD", "REQ-001", "MISSING", "implemented_by"))

    def test_direct_relationship_traversal_is_bidirectional(self):
        cell = build_demo_cell()
        related = cell.related_records("REQ-001")
        self.assertEqual([item.record_id for item in related], ["CTRL-001"])

    def test_invalid_layer_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown GRC layer"):
            GRCRecord("BAD", "policy", "not_a_layer", "Invalid")


class SignalEngineTests(unittest.TestCase):
    def test_requirement_change_routes_impact_signal_and_records_history(self):
        cell = build_demo_cell()
        bus = SignalBus()
        bus.subscribe("requirement.changed", requirement_change_handler)
        original = GRCSignal(
            "requirement.changed", "test",
            {"record_id": "REQ-001", "change_summary": "Frequency changed"},
        )
        events = bus.publish(cell, original)
        self.assertEqual([item.signal_type for item in events], [
            "requirement.changed", "requirement.impact_assessed",
        ])
        impact = events[1]
        self.assertEqual(impact.payload["candidate_impact_ids"], ["CTRL-001"])
        self.assertTrue(impact.payload["requires_review"])
        self.assertEqual(impact.parent_signal_id, original.signal_id)
        self.assertEqual(cell.signal_history, events)

    def test_unknown_requirement_fails_closed(self):
        cell = build_demo_cell()
        bus = SignalBus()
        bus.subscribe("requirement.changed", requirement_change_handler)
        with self.assertRaisesRegex(ValueError, "known record"):
            bus.publish(cell, GRCSignal(
                "requirement.changed", "test", {"record_id": "MISSING"},
            ))

    def test_duplicate_signal_id_is_rejected(self):
        cell = build_demo_cell()
        signal = GRCSignal("unhandled.event", "test", signal_id="DUP")
        bus = SignalBus()
        bus.publish(cell, signal)
        with self.assertRaisesRegex(ValueError, "Duplicate signal ID"):
            bus.publish(cell, signal)

    def test_event_loop_is_bounded(self):
        cell = build_demo_cell()
        bus = SignalBus(max_events_per_publish=2)
        bus.subscribe("loop", lambda _cell, signal: [GRCSignal(
            "loop", "test", parent_signal_id=signal.signal_id,
        )])
        with self.assertRaisesRegex(RuntimeError, "processing limit"):
            bus.publish(cell, GRCSignal("loop", "test"))


if __name__ == "__main__":
    unittest.main()
