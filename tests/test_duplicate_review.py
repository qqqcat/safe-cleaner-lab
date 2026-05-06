from pathlib import Path

from safecleaner.duplicate_review import find_duplicates


def test_duplicate_review_finds_duplicates(tmp_path: Path) -> None:
    (tmp_path / "one.txt").write_text("same")
    (tmp_path / "two.txt").write_text("same")
    (tmp_path / "three.txt").write_text("different")

    groups, fallback_count = find_duplicates(str(tmp_path))

    assert fallback_count == 0
    assert len(groups) == 1
    assert len(groups[0].duplicates) == 1


def test_duplicate_hash_fallback_does_not_crash(tmp_path: Path, monkeypatch) -> None:
    f1 = tmp_path / "one.txt"
    f2 = tmp_path / "two.txt"
    f1.write_text("same")
    f2.write_text("same")

    original_open = Path.open

    def broken_open(self: Path, *args, **kwargs):
        if self.name in {"one.txt", "two.txt"}:
            raise OSError("hash read failed")
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", broken_open)

    groups, fallback_count = find_duplicates(str(tmp_path))

    assert len(groups) == 0
    assert fallback_count >= 2
