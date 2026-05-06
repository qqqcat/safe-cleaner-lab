from __future__ import annotations

import shutil
from pathlib import Path

from .models import CleanupReport, CleanupResultItem, FailureKind
from .staging import purge_staging, stage_target


def cleanup_path(path: str, mode: str) -> tuple[CleanupReport, str | None]:
    target = Path(path)
    root = target.parent
    report = CleanupReport()
    maintenance_feedback: str | None = None

    if not target.exists():
        report.items.append(
            CleanupResultItem(
                target=str(target),
                success=False,
                mode=mode,
                failure_kind=FailureKind.NOT_FOUND,
                message="target does not exist",
            )
        )
        return report, None

    try:
        if mode == "recycle":
            trash_dir = root / ".trash"
            trash_dir.mkdir(exist_ok=True)
            shutil.move(str(target), str(trash_dir / target.name))
        elif mode == "permanent":
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        elif mode == "fast":
            stage_target(root, target)
            maintenance = purge_staging(root)
            maintenance_feedback = maintenance.message
        else:
            raise ValueError(f"Unsupported mode: {mode}")

        report.items.append(CleanupResultItem(target=str(target), success=True, mode=mode, message="ok"))
    except FileNotFoundError:
        report.items.append(
            CleanupResultItem(
                target=str(target),
                success=False,
                mode=mode,
                failure_kind=FailureKind.NOT_FOUND,
                message="target disappeared before cleanup",
            )
        )
    except PermissionError:
        report.items.append(
            CleanupResultItem(
                target=str(target),
                success=False,
                mode=mode,
                failure_kind=FailureKind.PERMISSION,
                message="permission denied",
            )
        )
    except OSError as exc:
        report.items.append(
            CleanupResultItem(
                target=str(target),
                success=False,
                mode=mode,
                failure_kind=FailureKind.IO,
                message=str(exc),
            )
        )
    return report, maintenance_feedback
