import unicodedata

from vault.scan import scan_vault


def build(root, *names):
    """Create every `name` as a file under `root`."""
    for name in names:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("body", encoding="utf-8")
    return root


def test_lists_every_markdown_file(tmp_path):
    build(tmp_path, "CIDR.md", "200 Dev/Subnet mask.md")
    paths, _ = scan_vault(tmp_path)
    assert paths == ["200 Dev/Subnet mask.md", "CIDR.md"]


def test_ignores_a_file_that_is_not_markdown(tmp_path):
    build(tmp_path, "CIDR.md", "diagram.png", "notes.txt")
    paths, _ = scan_vault(tmp_path)
    assert paths == ["CIDR.md"]


def test_ignores_a_dot_directory(tmp_path):
    build(tmp_path, "CIDR.md", ".obsidian/workspace.md", ".git/COMMIT.md")
    paths, _ = scan_vault(tmp_path)
    assert paths == ["CIDR.md"]


def test_indexes_a_file_by_its_name_without_the_extension(tmp_path):
    build(tmp_path, "200 Dev/CIDR.md")
    _, index = scan_vault(tmp_path)
    assert index["CIDR"] == ["200 Dev/CIDR.md"]


def test_a_name_maps_to_every_file_that_carries_it(tmp_path):
    build(tmp_path, "000 Index/Hub.md", "500 Mind/Hub.md")
    _, index = scan_vault(tmp_path)
    assert index["Hub"] == ["000 Index/Hub.md", "500 Mind/Hub.md"]


def test_a_dot_inside_the_name_survives(tmp_path):
    build(tmp_path, "No.013 philosopher stone.md")
    _, index = scan_vault(tmp_path)
    assert "No.013 philosopher stone" in index


def test_a_name_is_indexed_in_nfc(tmp_path):
    build(tmp_path, unicodedata.normalize("NFD", "한글") + ".md")
    _, index = scan_vault(tmp_path)
    assert "한글" in index
