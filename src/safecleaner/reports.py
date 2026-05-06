from __future__ import annotations

from .models import CleanupReport


def format_cleanup_report(report: CleanupReport) -> str:
    lines = [
        f"Cleanup results: success={report.success_count} failure={report.failure_count}",
    ]
    for item in report.items:
        status = "OK" if item.success else "FAIL"
        lines.append(f"- [{status}] {item.mode} {item.target} :: {item.message}")
    return "\n".join(lines)
