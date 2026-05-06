from __future__ import annotations

from dataclasses import dataclass, field

from .duplicate_result import DuplicateReviewResult
from .models import CleanupReport, MaintenanceResult, ScanError
from .notifier import UserNotice


@dataclass
class SessionState:
    """Per-process state that stitches command runs together for demo/reporting."""

    last_scan_errors: list[ScanError] = field(default_factory=list)
    last_cleanup_report: CleanupReport | None = None
    last_duplicate_result: DuplicateReviewResult | None = None
    last_maintenance_result: MaintenanceResult | None = None
    user_notices: list[UserNotice] = field(default_factory=list)

    def record_notices(self, notices: list[UserNotice]) -> None:
        self.user_notices.extend(notices)
