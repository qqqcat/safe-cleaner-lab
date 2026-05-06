from __future__ import annotations

import hashlib
from collections import defaultdict
from pathlib import Path

from .duplicate_result import DuplicateReviewResult
from .models import DuplicateGroup


def _hash_file(path: Path) -> tuple[str, bool]:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(8192), b""):
                digest.update(chunk)
        return digest.hexdigest(), False
    except Exception:
        # TODO: wire duplicate hash fallback detail into telemetry/diagnostics pipeline.
        fallback = hashlib.sha256(str(path).encode("utf-8")).hexdigest()
        return fallback, True


def find_duplicates(path: str) -> DuplicateReviewResult:
    base = Path(path)
    by_size: dict[int, list[Path]] = defaultdict(list)

    for entry in base.rglob("*"):
        if entry.is_file():
            by_size[entry.stat().st_size].append(entry)

    groups: list[DuplicateGroup] = []
    fallback_hits = 0

    for same_size in by_size.values():
        if len(same_size) < 2:
            continue
        by_hash: dict[str, list[Path]] = defaultdict(list)
        for file_path in same_size:
            h, used_fallback = _hash_file(file_path)
            if used_fallback:
                fallback_hits += 1
            by_hash[h].append(file_path)

        for files in by_hash.values():
            if len(files) > 1:
                sorted_files = sorted(str(f) for f in files)
                groups.append(DuplicateGroup(keep=sorted_files[0], duplicates=sorted_files[1:]))

    return DuplicateReviewResult(groups=groups, fallback_count=fallback_hits, skipped_paths=[])
