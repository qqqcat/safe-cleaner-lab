from __future__ import annotations

from pathlib import Path

from .models import ScanError


def classify_scan_exception(exc: Exception) -> str:
    if isinstance(exc, FileNotFoundError):
        return "user"
    if isinstance(exc, TimeoutError):
        return "transient"
    return "system"


def scan_path(path: str) -> tuple[list[str], list[ScanError]]:
    target = Path(path)
    files: list[str] = []
    errors: list[ScanError] = []

    if not target.exists():
        errors.append(ScanError(path=str(target), kind="user", message="path does not exist"))
        return files, errors

    try:
        for entry in target.rglob("*"):
            if entry.is_file():
                files.append(str(entry))
    except Exception as exc:  # realistic boundary
        errors.append(
            ScanError(path=str(target), kind=classify_scan_exception(exc), message=str(exc))
        )

    return files, errors
