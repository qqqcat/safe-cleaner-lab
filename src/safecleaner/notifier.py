from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import CleanupReport, MaintenanceResult


class NoticeLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class UserNotice:
    level: NoticeLevel
    summary: str


def notices_from_cleanup_report(report: CleanupReport) -> list[UserNotice]:
    notices: list[UserNotice] = []
    if report.failure_count > 0:
        notices.append(UserNotice(level=NoticeLevel.WARNING, summary=f"Cleanup finished with {report.failure_count} failure(s)."))
    elif report.success_count > 0:
        notices.append(UserNotice(level=NoticeLevel.INFO, summary="Cleanup finished successfully."))
    return notices


def notices_from_maintenance_result(result: MaintenanceResult | None) -> list[UserNotice]:
    if result is None:
        return []
    if result.success:
        return [UserNotice(level=NoticeLevel.INFO, summary=result.message)]
    return [UserNotice(level=NoticeLevel.WARNING, summary=result.message)]


def render_notice(notice: UserNotice) -> str:
    return f"Notice[{notice.level.value.upper()}] {notice.summary}"
