from __future__ import annotations

import argparse
import json
from pathlib import Path

from .cleanup import cleanup_path
from .cleanup_finalizer import finalize_cleanup
from .diagnostics import diagnostics_snapshot
from .duplicate_review import find_duplicates
from .maintenance_audit import MaintenanceAuditLog
from .notifier import (
    notices_from_cleanup_report,
    notices_from_maintenance_result,
    render_notice,
)
from .report_store import ReportStore
from .reports import format_cleanup_report
from .scanner import scan_path
from .session_state import SessionState
from .staging import purge_staging
from .telemetry import GLOBAL_TELEMETRY

SESSION_STATE = SessionState()
REPORT_STORE = ReportStore()
MAINTENANCE_AUDIT = MaintenanceAuditLog()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="safecleaner", description="Safe Cleaner Lab CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("demo", help="run demo diagnostics output")

    scan = sub.add_parser("scan", help="scan a path")
    scan.add_argument("path")

    cleanup = sub.add_parser("cleanup", help="cleanup a target path")
    cleanup.add_argument("path")
    cleanup.add_argument("--mode", choices=["recycle", "fast", "permanent"], required=True)

    dup = sub.add_parser("duplicates", help="find duplicate files")
    dup.add_argument("path")

    m = sub.add_parser("maintenance", help="purge staging directory")
    m.add_argument("path")

    sub.add_parser("report", help="print diagnostics snapshot")
    return parser


def run_cli(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "demo":
        print("Safe Cleaner Lab demo")
        print(json.dumps(diagnostics_snapshot(GLOBAL_TELEMETRY, SESSION_STATE, REPORT_STORE), indent=2))
        return 0

    if args.command == "scan":
        files, errors = scan_path(args.path)
        SESSION_STATE.last_scan_errors = errors
        GLOBAL_TELEMETRY.scan_error_count += len(errors)
        print(f"Found {len(files)} files")
        for err in errors:
            print(f"ScanError[{err.kind}]: {err.path} ({err.message})")
        return 0

    if args.command == "cleanup":
        report, maintenance_result = cleanup_path(args.path, args.mode)
        REPORT_STORE.remember_cleanup(report)
        finalize_cleanup(report, maintenance_result, SESSION_STATE, GLOBAL_TELEMETRY)
        notices = notices_from_cleanup_report(report) + notices_from_maintenance_result(maintenance_result)
        SESSION_STATE.record_notices(notices)
        GLOBAL_TELEMETRY.user_notice_count += len(notices)

        print(format_cleanup_report(report))
        for notice in notices:
            print(render_notice(notice))
        return 0 if report.failure_count == 0 else 1

    if args.command == "duplicates":
        result = find_duplicates(args.path)
        SESSION_STATE.last_duplicate_result = result
        REPORT_STORE.remember_duplicate_result(result)
        GLOBAL_TELEMETRY.duplicate_group_count = len(result.groups)
        GLOBAL_TELEMETRY.duplicate_fallback_count += result.fallback_count
        GLOBAL_TELEMETRY.duplicate_skipped_count += len(result.skipped_paths)
        print(f"Duplicate groups: {len(result.groups)}")
        for grp in result.groups:
            print(f"Keep: {grp.keep}")
            for dup in grp.duplicates:
                print(f"  duplicate: {dup}")
        return 0

    if args.command == "maintenance":
        result = purge_staging(Path(args.path))
        SESSION_STATE.last_maintenance_result = result
        GLOBAL_TELEMETRY.maintenance_runs += 1
        if not result.success:
            GLOBAL_TELEMETRY.maintenance_failed += 1
        GLOBAL_TELEMETRY.last_maintenance_feedback = result.message
        MAINTENANCE_AUDIT.record("purge_staging", result.success)

        notices = notices_from_maintenance_result(result)
        SESSION_STATE.record_notices(notices)
        GLOBAL_TELEMETRY.user_notice_count += len(notices)

        print(result.message)
        for notice in notices:
            print(render_notice(notice))
        return 0 if result.success else 1

    if args.command == "report":
        print(json.dumps(diagnostics_snapshot(GLOBAL_TELEMETRY, SESSION_STATE, REPORT_STORE), indent=2))
        return 0

    return 1
