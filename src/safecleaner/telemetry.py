from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class Telemetry:
    scan_error_count: int = 0
    cleanup_attempted: int = 0
    cleanup_failed: int = 0
    maintenance_runs: int = 0
    duplicate_fallback_count: int = 0
    duplicate_group_count: int = 0
    cleanup_audit_tail: deque[str] = field(default_factory=lambda: deque(maxlen=20))
    last_maintenance_feedback: str = ""

    def audit_cleanup(self, entry: str) -> None:
        self.cleanup_audit_tail.append(entry)


GLOBAL_TELEMETRY = Telemetry()
