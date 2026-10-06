import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scrub_check import scan  # noqa: E402


def test_detects_personal_term(tmp_path):
    f = tmp_path / "notes.md"
    f.write_text("contact jane.doe@example.com today")
    assert scan([f], {"jane.doe@example.com"})


def test_blocks_private_folder(tmp_path):
    f = tmp_path / "private" / "profile.yaml"
    f.parent.mkdir()
    f.write_text("x")
    assert scan([f], set())


def test_clean_file_passes(tmp_path):
    f = tmp_path / "ok.md"
    f.write_text("Alex Sample")
    assert scan([f], {"jane.doe@example.com"}) == []
