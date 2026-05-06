from safecleaner.cleanup_finalizer import finalize_cleanup
from safecleaner.diagnostics import diagnostics_snapshot
from safecleaner.maintenance_audit import MaintenanceAuditLog
from safecleaner.models import CleanupReport, CleanupResultItem, MaintenanceResult
from safecleaner.notifier import notices_from_maintenance_result
from safecleaner.report_store import ReportStore
from safecleaner.session_state import SessionState
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


def test_diagnostics_omits_duplicate_fallback_count() -> None:
    telemetry = Telemetry(duplicate_fallback_count=9)
    snapshot = diagnostics_snapshot(telemetry)
    assert "duplicate_fallback_count" not in snapshot


def test_fast_cleanup_purge_failure_increments_telemetry_without_report_failure() -> None:
    telemetry = Telemetry()
    state = SessionState()
    report = CleanupReport(items=[CleanupResultItem(target="/tmp/x", success=True, mode="fast", message="ok")])
    maintenance = MaintenanceResult(message="Staging purge failed: disk busy", success=False)

    finalize_cleanup(report, maintenance, state, telemetry)

    assert report.failure_count == 0
    assert telemetry.fast_purge_attempted == 1
    assert telemetry.fast_purge_failed == 1


def test_maintenance_audit_records_failures_but_not_in_diagnostics() -> None:
    telemetry = Telemetry(last_maintenance_feedback="Staging purge failed")
    audit = MaintenanceAuditLog()
    audit.record("purge_staging", success=False)

    snapshot = diagnostics_snapshot(telemetry)

    assert audit.tail()
    assert "maintenance_audit_tail" not in snapshot


def test_user_notices_for_maintenance_warning_not_in_diagnostics() -> None:
    telemetry = Telemetry(last_maintenance_feedback="Staging purge failed")
    state = SessionState()
    notices = notices_from_maintenance_result(MaintenanceResult(message="Staging purge failed", success=False))
    state.record_notices(notices)
    telemetry.user_notice_count = len(notices)

    snapshot = diagnostics_snapshot(telemetry, state, ReportStore())

    assert notices
    assert notices[0].level.value == "warning"
    assert "user_notices" not in snapshot
