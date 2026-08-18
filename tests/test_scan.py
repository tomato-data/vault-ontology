import unicodedata

from vault.scan import case_collisions, duplicate_names, resolve_link, scan_vault


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


PATHS = [
    "000 Index/Hub.md",
    "200 Dev/CIDR.md",
    "200 Dev/Network/Subnet mask.md",
    "200 Dev/한글.md",
    "500 Mind/Hub.md",
]
INDEX = {
    "Hub": ["000 Index/Hub.md", "500 Mind/Hub.md"],
    "CIDR": ["200 Dev/CIDR.md"],
    "Subnet mask": ["200 Dev/Network/Subnet mask.md"],
    "한글": ["200 Dev/한글.md"],
}


def test_resolves_a_plain_name():
    assert resolve_link("CIDR", INDEX, PATHS) == "200 Dev/CIDR.md"


def test_returns_none_for_a_name_that_is_not_there():
    assert resolve_link("nothing here", INDEX, PATHS) is None


def test_a_repeated_name_always_picks_the_same_one():
    assert resolve_link("Hub", INDEX, PATHS) == "000 Index/Hub.md"


def test_a_path_tells_the_two_apart():
    assert resolve_link("500 Mind/Hub", INDEX, PATHS) == "500 Mind/Hub.md"


def test_a_partial_path_matches_the_tail():
    assert (
        resolve_link("Network/Subnet mask", INDEX, PATHS)
        == "200 Dev/Network/Subnet mask.md"
    )


def test_a_tail_match_starts_at_a_directory_boundary():
    assert resolve_link("work/Subnet mask", INDEX, PATHS) is None


def test_a_decomposed_target_resolves():
    assert (
        resolve_link(unicodedata.normalize("NFD", "한글"), INDEX, PATHS)
        == "200 Dev/한글.md"
    )


def test_a_clean_index_has_no_duplicate():
    assert duplicate_names({"CIDR": ["200 Dev/CIDR.md"]}) == {}


def test_a_repeated_name_is_reported_with_every_path():
    assert duplicate_names(INDEX) == {"Hub": ["000 Index/Hub.md", "500 Mind/Hub.md"]}


def test_names_that_differ_only_by_case_collide():
    index = {"Python": ["200 Dev/Python.md"], "python": ["300 Run/python.md"]}
    assert case_collisions(index) == {"python": ["Python", "python"]}


def test_a_name_unique_ignoring_case_does_not_collide():
    index = {"Python": ["200 Dev/Python.md"], "Ruby": ["200 Dev/Ruby.md"]}
    assert case_collisions(index) == {}


def test_three_spellings_are_reported_as_one_collision():
    index = {"API": ["a/API.md"], "Api": ["b/Api.md"], "api": ["c/api.md"]}
    assert case_collisions(index) == {"api": ["API", "Api", "api"]}


def test_a_repeated_name_is_not_a_case_collision():
    assert case_collisions(INDEX) == {}
