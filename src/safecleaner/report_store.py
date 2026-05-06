from __future__ import annotations

from dataclasses import dataclass

from .duplicate_result import DuplicateReviewResult
from .models import CleanupReport


@dataclass
class ReportStore:
    last_cleanup_report: CleanupReport | None = None
    last_duplicate_result: DuplicateReviewResult | None = None

    def remember_cleanup(self, report: CleanupReport) -> None:
        self.last_cleanup_report = report

    def remember_duplicate_result(self, result: DuplicateReviewResult) -> None:
        self.last_duplicate_result = result

    def cleanup_summary(self) -> dict[str, int]:
        if self.last_cleanup_report is None:
            return {"attempted": 0, "failed": 0}
        return {
            "attempted": len(self.last_cleanup_report.items),
            "failed": self.last_cleanup_report.failure_count,
        }

    def duplicate_summary(self) -> dict[str, int]:
        if self.last_duplicate_result is None:
            return {"group_count": 0}
        return {"group_count": len(self.last_duplicate_result.groups)}
