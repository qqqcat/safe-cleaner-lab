from safecleaner.diagnostics import diagnostics_snapshot
from safecleaner.telemetry import Telemetry


def test_diagnostics_contains_cleanup_counters() -> None:
    telemetry = Telemetry()
    telemetry.cleanup_attempted = 3
    telemetry.cleanup_failed = 1
    telemetry.scan_error_count = 2
    telemetry.duplicate_group_count = 4
    telemetry.last_maintenance_feedback = "Staging purge completed"
    telemetry.audit_cleanup("mode=recycle success=True")

    snapshot = diagnostics_snapshot(telemetry)

    assert snapshot["cleanup_attempted"] == 3
    assert snapshot["cleanup_failed"] == 1
    assert snapshot["scan_error_count"] == 2
    assert snapshot["duplicate_group_count"] == 4
    assert snapshot["cleanup_audit_tail"]
