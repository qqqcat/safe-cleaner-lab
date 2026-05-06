from pathlib import Path

from safecleaner.staging import purge_staging, stage_target


def test_staging_maintenance_returns_coarse_feedback(tmp_path: Path) -> None:
    target = tmp_path / "temp.txt"
    target.write_text("x")
    stage_target(tmp_path, target)

    result = purge_staging(tmp_path)

    assert result.success is True
    assert "completed" in result.message.lower()


def test_maintenance_succeeds_without_staging_dir(tmp_path: Path) -> None:
    result = purge_staging(tmp_path)
    assert result.success is True
    assert "No staging" in result.message
