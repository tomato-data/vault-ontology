import json

from vault.lint import load_rules, skips_frontmatter, skips_unresolved


RULES = {
    "skip_unresolved_from": ["300 Runtime/301 Day Notes"],
    "skip_unresolved_to": ["...", "참조"],
    "skip_frontmatter_in": ["800 TRPG"],
    "skip_files": ["000 Index/Daily Template.md"],
}


def test_an_absent_config_gives_the_defaults(tmp_path):
    rules = load_rules(tmp_path)
    assert rules == {
        "skip_unresolved_from": [],
        "skip_unresolved_to": [],
        "skip_frontmatter_in": [],
        "skip_files": [],
    }


def test_a_config_file_is_read(tmp_path):
    (tmp_path / ".vault-lint.json").write_text(
        json.dumps({"skip_files": ["a.md"]}), encoding="utf-8"
    )
    assert load_rules(tmp_path)["skip_files"] == ["a.md"]


def test_a_partial_config_keeps_the_other_defaults(tmp_path):
    (tmp_path / ".vault-lint.json").write_text(
        json.dumps({"skip_files": ["a.md"]}), encoding="utf-8"
    )
    assert load_rules(tmp_path)["skip_unresolved_to"] == []


def test_frontmatter_is_skipped_inside_a_listed_zone():
    assert skips_frontmatter(RULES, "800 TRPG/완제품/현자의 돌.md")


def test_frontmatter_is_checked_in_a_zone_that_only_skips_links():
    assert not skips_frontmatter(RULES, "300 Runtime/301 Day Notes/2026-04-17.md")


def test_an_unresolved_link_from_a_listed_zone_is_skipped():
    assert skips_unresolved(
        RULES, "300 Runtime/301 Day Notes/2026-04-17.md", "옛 계획서"
    )


def test_an_unresolved_link_to_a_placeholder_is_skipped():
    assert skips_unresolved(RULES, "200 Dev/CIDR.md", "...")


def test_an_unresolved_link_matching_neither_is_reported():
    assert not skips_unresolved(RULES, "200 Dev/CIDR.md", "없는 문서")


def test_a_skipped_file_is_skipped_by_both():
    path = "000 Index/Daily Template.md"
    assert skips_frontmatter(RULES, path)
    assert skips_unresolved(RULES, path, "없는 문서")


def test_a_zone_prefix_stops_at_a_directory_boundary():
    rules = {**RULES, "skip_frontmatter_in": ["800 TRPG"]}
    assert not skips_frontmatter(rules, "800 TRPG Archive/x.md")
