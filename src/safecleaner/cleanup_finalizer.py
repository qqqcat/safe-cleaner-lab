from __future__ import annotations

from .models import CleanupReport, MaintenanceResult
from .session_state import SessionState
from .telemetry import Telemetry


def finalize_cleanup(
    report: CleanupReport,
    maintenance_result: MaintenanceResult | None,
    state: SessionState,
    telemetry: Telemetry,
) -> None:
    state.last_cleanup_report = report
    state.last_maintenance_result = maintenance_result

    for item in report.items:
        telemetry.cleanup_attempted += 1
        if not item.success:
            telemetry.cleanup_failed += 1
        telemetry.audit_cleanup(f"mode={item.mode} target={item.target} success={item.success}")

    if maintenance_result is not None:
        telemetry.maintenance_runs += 1
        telemetry.last_maintenance_feedback = maintenance_result.message

        telemetry.fast_purge_attempted += 1
        if not maintenance_result.success:
            telemetry.fast_purge_failed += 1
            telemetry.maintenance_failed += 1
            # TODO: fast cleanup purge failures are not merged into CleanupReport.
