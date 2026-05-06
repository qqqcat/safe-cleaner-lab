from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class FailureKind(str, Enum):
    NOT_FOUND = "not_found"
    PERMISSION = "permission"
    IO = "io"
    UNKNOWN = "unknown"


class Visibility(str, Enum):
    USER = "user"
    INTERNAL = "internal"


@dataclass
class CleanupResultItem:
    target: str
    success: bool
    mode: str
    failure_kind: FailureKind | None = None
    visibility: Visibility = Visibility.USER
    message: str = ""


@dataclass
class CleanupReport:
    items: list[CleanupResultItem] = field(default_factory=list)

    @property
    def success_count(self) -> int:
        return sum(1 for item in self.items if item.success)

    @property
    def failure_count(self) -> int:
        return sum(1 for item in self.items if not item.success)


@dataclass
class ScanError:
    path: str
    kind: str
    message: str


@dataclass
class DuplicateGroup:
    keep: str
    duplicates: list[str]


@dataclass
class MaintenanceResult:
    message: str
    success: bool
