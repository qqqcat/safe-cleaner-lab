from __future__ import annotations

import argparse
import json
from pathlib import Path

from .cleanup import cleanup_path
from .diagnostics import diagnostics_snapshot
from .duplicate_review import find_duplicates
from .reports import format_cleanup_report
from .scanner import scan_path
from .staging import purge_staging
from .telemetry import GLOBAL_TELEMETRY


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
        print(json.dumps(diagnostics_snapshot(GLOBAL_TELEMETRY), indent=2))
        return 0

    if args.command == "scan":
        files, errors = scan_path(args.path)
        GLOBAL_TELEMETRY.scan_error_count += len(errors)
        print(f"Found {len(files)} files")
        for err in errors:
            print(f"ScanError[{err.kind}]: {err.path} ({err.message})")
        return 0

    if args.command == "cleanup":
        report, maintenance_feedback = cleanup_path(args.path, args.mode)
        for item in report.items:
            GLOBAL_TELEMETRY.cleanup_attempted += 1
            if not item.success:
                GLOBAL_TELEMETRY.cleanup_failed += 1
            GLOBAL_TELEMETRY.audit_cleanup(
                f"mode={item.mode} target={item.target} success={item.success}"
            )
        if maintenance_feedback:
            GLOBAL_TELEMETRY.last_maintenance_feedback = maintenance_feedback
        print(format_cleanup_report(report))
        return 0 if report.failure_count == 0 else 1

    if args.command == "duplicates":
        groups, fallback_count = find_duplicates(args.path)
        GLOBAL_TELEMETRY.duplicate_group_count = len(groups)
        GLOBAL_TELEMETRY.duplicate_fallback_count += fallback_count
        print(f"Duplicate groups: {len(groups)}")
        for grp in groups:
            print(f"Keep: {grp.keep}")
            for dup in grp.duplicates:
                print(f"  duplicate: {dup}")
        return 0

    if args.command == "maintenance":
        result = purge_staging(Path(args.path))
        GLOBAL_TELEMETRY.maintenance_runs += 1
        GLOBAL_TELEMETRY.last_maintenance_feedback = result.message
        print(result.message)
        return 0 if result.success else 1

    if args.command == "report":
        print(json.dumps(diagnostics_snapshot(GLOBAL_TELEMETRY), indent=2))
        return 0

    return 1
