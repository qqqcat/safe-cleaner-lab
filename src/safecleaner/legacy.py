from __future__ import annotations

from pathlib import Path


def delete_direct_legacy(path: str) -> bool:
    target = Path(path)
    if not target.exists():
        return False
    if target.is_dir():
        for child in target.iterdir():
            if child.is_file():
                child.unlink()
        target.rmdir()
    else:
        target.unlink()
    return True
