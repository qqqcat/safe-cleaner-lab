from __future__ import annotations

import shutil
from pathlib import Path

from .models import MaintenanceResult


def stage_target(root: Path, target: Path) -> Path:
    staging_dir = root / ".staging"
    staging_dir.mkdir(exist_ok=True)
    staged_path = staging_dir / target.name
    if staged_path.exists():
        if staged_path.is_dir():
            shutil.rmtree(staged_path)
        else:
            staged_path.unlink()
    shutil.move(str(target), str(staged_path))
    return staged_path


def purge_staging(root: Path) -> MaintenanceResult:
    staging_dir = root / ".staging"
    if not staging_dir.exists():
        return MaintenanceResult(message="No staging directory found", success=True)

    try:
        for child in list(staging_dir.iterdir()):
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
        # TODO: emit structured FailureKind records for per-item purge failures.
        return MaintenanceResult(message="Staging purge completed", success=True)
    except Exception as exc:
        return MaintenanceResult(message=f"Staging purge failed: {exc}", success=False)
