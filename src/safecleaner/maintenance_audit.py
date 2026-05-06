from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class MaintenanceAuditLog:
    entries: deque[str] = field(default_factory=lambda: deque(maxlen=20))

    def record(self, operation: str, success: bool) -> None:
        self.entries.append(f"operation={operation} success={success}")

    def tail(self) -> list[str]:
        return list(self.entries)
