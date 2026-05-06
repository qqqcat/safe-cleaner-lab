from __future__ import annotations

from .diagnostic_sections import cleanup_section, duplicate_section, maintenance_section, scan_section
from .report_store import ReportStore
from .session_state import SessionState
from .telemetry import Telemetry


def diagnostics_snapshot(
    telemetry: Telemetry,
    state: SessionState | None = None,
    store: ReportStore | None = None,
) -> dict[str, object]:
    session_state = state or SessionState()
    report_store = store or ReportStore()
    snapshot: dict[str, object] = {}
    snapshot.update(scan_section(telemetry))
    snapshot.update(cleanup_section(telemetry, report_store))
    snapshot.update(duplicate_section(telemetry, report_store))
    snapshot.update(maintenance_section(telemetry, session_state))
    return snapshot
