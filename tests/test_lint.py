import json

from vault.__main__ import main
from vault.lint import (
    lint_vault,
    load_rules,
    skips_frontmatter,
    skips_unresolved,
)
from vault.graph import build, find

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


GOOD = "---\ntype: concept\nsummary: ok\ncreated: 2026-08-10\n---\n본문\n"


def build_vault(root, files):
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def codes_of(root):
    return sorted((path, code) for path, code, _ in lint_vault(root))


def test_a_clean_vault_reports_nothing(tmp_path):
    build_vault(tmp_path, {"CIDR.md": GOOD})
    assert lint_vault(tmp_path) == []


def test_an_unknown_type_is_reported_with_its_path(tmp_path):
    build_vault(tmp_path, {"a.md": "---\ntype: essay\ncreated: 2026-08-10\n---\n본문\n"})
    assert codes_of(tmp_path) == [("a.md", "type unknown")]


def test_a_body_tag_is_reported(tmp_path):
    build_vault(tmp_path, {"a.md": GOOD.replace("본문", "#Stack/Python 쓴다")})
    assert codes_of(tmp_path) == [("a.md", "body tag")]


def test_a_builds_on_that_lands_is_not_reported(tmp_path):
    build_vault(
        tmp_path,
        {
            "a.md": GOOD.replace("---\n본문", 'builds_on:\n  - "[[CIDR]]"\n---\n본문'),
            "CIDR.md": GOOD,
        },
    )
    assert lint_vault(tmp_path) == []


def test_a_builds_on_that_does_not_land_is_reported(tmp_path):
    build_vault(
        tmp_path,
        {
            "a.md": GOOD.replace(
                "---\n본문", 'builds_on:\n  - "[[없는 문서]]"\n---\n본문'
            ),
        },
    )
    assert codes_of(tmp_path) == [("a.md", "builds_on unresolved")]


def test_an_unresolved_body_link_is_reported(tmp_path):
    build_vault(tmp_path, {"a.md": GOOD.replace("본문", "[[없는 문서]] 참조")})
    assert codes_of(tmp_path) == [("a.md", "link unresolved")]


def test_a_link_skip_leaves_the_frontmatter_checks_on(tmp_path):
    build_vault(
        tmp_path,
        {
            ".vault-lint.json": '{"skip_unresolved_from": ["Day"]}',
            "Day/a.md": "---\ntype: essay\ncreated: 2026-08-10\n---\n[[없는 문서]]\n",
        },
    )
    assert codes_of(tmp_path) == [("Day/a.md", "type unknown")]


def test_a_frontmatter_skip_leaves_the_link_checks_on(tmp_path):
    build_vault(
        tmp_path,
        {
            ".vault-lint.json": '{"skip_frontmatter_in": ["TRPG"]}',
            "TRPG/a.md": "---\ntype: essay\ncreated: 2026-08-10\n---\n[[없는 문서]]\n",
        },
    )
    assert codes_of(tmp_path) == [("TRPG/a.md", "link unresolved")]


def test_main_returns_zero_on_a_clean_vault(tmp_path):
    build_vault(tmp_path, {"CIDR.md": GOOD})
    assert main(["lint", "--vault", str(tmp_path)]) == 0


def test_main_returns_one_when_something_is_wrong(tmp_path):
    build_vault(tmp_path, {"a.md": "---\ntype: essay\ncreated: 2026-08-10\n---\n본문\n"})
    assert main(["lint", "--vault", str(tmp_path)]) == 1


def test_main_returns_two_for_a_vault_that_is_not_there(tmp_path):
    assert main(["lint", "--vault", str(tmp_path / "없음")]) == 2


def test_find_takes_a_name(tmp_path):
    db = build(build_vault(tmp_path, {"200 Dev/CIDR.md": GOOD}))
    assert find(db, "CIDR") == "200 Dev/CIDR.md"


def test_find_takes_a_path(tmp_path):
    db = build(build_vault(tmp_path, {"200 Dev/CIDR.md": GOOD}))
    assert find(db, "200 Dev/CIDR.md") == "200 Dev/CIDR.md"


def test_find_returns_none_for_a_stranger(tmp_path):
    db = build(build_vault(tmp_path, {"CIDR.md": GOOD}))
    assert find(db, "없는 문서") is None


def test_build_writes_a_database(tmp_path):
    build_vault(tmp_path, {"CIDR.md": GOOD})
    assert main(["build", "--vault", str(tmp_path)]) == 0
    assert (tmp_path / ".vault-graph.db").exists()


def test_a_query_without_a_database_asks_you_to_build(tmp_path):
    build_vault(tmp_path, {"CIDR.md": GOOD})
    assert main(["q", "stats", "--vault", str(tmp_path)]) == 2


def test_a_query_after_a_build_succeeds(tmp_path):
    build_vault(tmp_path, {"CIDR.md": GOOD})
    main(["build", "--vault", str(tmp_path)])
    assert main(["q", "stats", "--vault", str(tmp_path)]) == 0


def test_a_query_about_an_unknown_note_returns_two(tmp_path):
    build_vault(tmp_path, {"CIDR.md": GOOD})
    main(["build", "--vault", str(tmp_path)])
    assert main(["q", "path", "없는 문서", "--vault", str(tmp_path)]) == 2
