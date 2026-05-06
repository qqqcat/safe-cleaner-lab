from pathlib import Path

from safecleaner.cleanup import cleanup_path


def test_recycle_moves_file_to_trash(tmp_path: Path) -> None:
    target = tmp_path / "a.txt"
    target.write_text("hello")

    report, _ = cleanup_path(str(target), "recycle")

    assert report.failure_count == 0
    assert not target.exists()
    assert (tmp_path / ".trash" / "a.txt").exists()


def test_permanent_deletes_file(tmp_path: Path) -> None:
    target = tmp_path / "dead.txt"
    target.write_text("gone")

    report, _ = cleanup_path(str(target), "permanent")

    assert report.failure_count == 0
    assert not target.exists()


def test_fast_cleanup_stages_then_purges(tmp_path: Path) -> None:
    target = tmp_path / "fast.txt"
    target.write_text("data")

    report, feedback = cleanup_path(str(target), "fast")

    assert report.failure_count == 0
    assert feedback is not None
    assert feedback.message == "Staging purge completed"
    assert not target.exists()
    staging = tmp_path / ".staging"
    assert staging.exists()
    assert list(staging.iterdir()) == []


def test_missing_cleanup_target_is_reported(tmp_path: Path) -> None:
    missing = tmp_path / "missing.txt"

    report, _ = cleanup_path(str(missing), "recycle")

    assert report.failure_count == 1
    assert report.items[0].message == "target does not exist"
