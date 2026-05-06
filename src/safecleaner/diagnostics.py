from __future__ import annotations

from .telemetry import Telemetry


def diagnostics_snapshot(telemetry: Telemetry) -> dict[str, object]:
    return {
        "scan_error_count": telemetry.scan_error_count,
        "cleanup_attempted": telemetry.cleanup_attempted,
        "cleanup_failed": telemetry.cleanup_failed,
        "duplicate_group_count": telemetry.duplicate_group_count,
        "last_maintenance_feedback": telemetry.last_maintenance_feedback,
        "cleanup_audit_tail": list(telemetry.cleanup_audit_tail),
    }
