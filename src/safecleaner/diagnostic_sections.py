from __future__ import annotations

from .report_store import ReportStore
from .session_state import SessionState
from .telemetry import Telemetry


def scan_section(telemetry: Telemetry) -> dict[str, int]:
    return {"scan_error_count": telemetry.scan_error_count}


def cleanup_section(telemetry: Telemetry, store: ReportStore) -> dict[str, object]:
    summary = store.cleanup_summary()
    return {
        "cleanup_attempted": max(telemetry.cleanup_attempted, summary["attempted"]),
        "cleanup_failed": max(telemetry.cleanup_failed, summary["failed"]),
        "cleanup_audit_tail": list(telemetry.cleanup_audit_tail),
    }


def duplicate_section(telemetry: Telemetry, store: ReportStore) -> dict[str, int]:
    summary = store.duplicate_summary()
    return {"duplicate_group_count": max(telemetry.duplicate_group_count, summary["group_count"])}


def maintenance_section(telemetry: Telemetry, _state: SessionState) -> dict[str, str]:
    return {"last_maintenance_feedback": telemetry.last_maintenance_feedback}
