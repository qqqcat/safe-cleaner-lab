from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup


@dataclass
class DuplicateReviewResult:
    groups: list[DuplicateGroup] = field(default_factory=list)
    fallback_count: int = 0
    skipped_paths: list[str] = field(default_factory=list)
