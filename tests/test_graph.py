from vault.graph import build

NOTE = "---\ntype: concept\nsummary: ok\ncreated: 2026-08-10\n---\n{body}\n"


def make(root, files):
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def rows(connection, sql):
    return connection.execute(sql).fetchall()


def test_a_note_becomes_a_node(tmp_path):
    make(tmp_path, {"200 Dev/CIDR.md": NOTE.format(body="본문")})
    db = build(tmp_path)
    assert rows(db, "SELECT path, name, zone, type FROM node") == [
        ("200 Dev/CIDR.md", "CIDR", "200 Dev", "concept")
    ]


def test_an_excluded_zone_is_not_a_node(tmp_path):
    make(
        tmp_path,
        {
            "CIDR.md": NOTE.format(body="본문"),
            "800 TRPG/현자의 돌.md": NOTE.format(body="본문"),
        },
    )
    assert rows(build(tmp_path), "SELECT path FROM node") == [("CIDR.md",)]


def test_claude_md_is_not_a_node(tmp_path):
    make(tmp_path, {"CIDR.md": NOTE.format(body="본문"), "CLAUDE.md": "지시문"})
    assert rows(build(tmp_path), "SELECT path FROM node") == [("CIDR.md",)]


def test_a_builds_on_becomes_an_edge(tmp_path):
    make(
        tmp_path,
        {
            "a.md": NOTE.format(body="본문").replace(
                "---\n본문", 'builds_on:\n  - "[[CIDR]]"\n---\n본문'
            ),
            "CIDR.md": NOTE.format(body="본문"),
        },
    )
    assert rows(build(tmp_path), "SELECT src, dst, kind FROM edge") == [
        ("a.md", "CIDR.md", "builds_on")
    ]


def test_a_body_link_becomes_a_links_to_edge(tmp_path):
    make(
        tmp_path,
        {
            "a.md": NOTE.format(body="[[CIDR]] 참조"),
            "CIDR.md": NOTE.format(body="본문"),
        },
    )
    assert rows(build(tmp_path), "SELECT src, dst, kind FROM edge") == [
        ("a.md", "CIDR.md", "links_to")
    ]


def test_a_frontmatter_link_is_not_counted_as_a_body_link(tmp_path):
    make(
        tmp_path,
        {
            "a.md": NOTE.format(body="본문").replace(
                "---\n본문", 'builds_on:\n  - "[[CIDR]]"\n---\n본문'
            ),
            "CIDR.md": NOTE.format(body="본문"),
        },
    )
    assert rows(build(tmp_path), "SELECT count(*) FROM edge") == [(1,)]


def test_an_unresolved_link_keeps_its_raw_and_a_null_dst(tmp_path):
    make(tmp_path, {"a.md": NOTE.format(body="[[없는 문서]] 참조")})
    assert rows(build(tmp_path), "SELECT dst, raw FROM edge") == [(None, "없는 문서")]


def test_a_link_into_an_excluded_zone_gets_a_null_dst(tmp_path):
    make(
        tmp_path,
        {
            "a.md": NOTE.format(body="[[현자의 돌]] 참조"),
            "800 TRPG/현자의 돌.md": NOTE.format(body="본문"),
        },
    )
    assert rows(build(tmp_path), "SELECT dst, raw FROM edge") == [(None, "현자의 돌")]


def test_an_embed_of_an_attachment_is_not_an_edge(tmp_path):
    make(tmp_path, {"a.md": NOTE.format(body="![[가상화.png]] 그림")})
    (tmp_path / "가상화.png").write_bytes(b"png")
    assert rows(build(tmp_path), "SELECT count(*) FROM edge") == [(0,)]


def test_a_tag_becomes_a_row(tmp_path):
    make(
        tmp_path,
        {
            "a.md": NOTE.format(body="본문").replace(
                "type: concept", "type: concept\ntags:\n  - Stack/Python"
            )
        },
    )
    assert rows(build(tmp_path), "SELECT path, tag FROM tag") == [
        ("a.md", "Stack/Python")
    ]


def test_building_twice_does_not_double_the_rows(tmp_path):
    make(tmp_path, {"CIDR.md": NOTE.format(body="본문")})
    database = tmp_path / "graph.db"
    build(tmp_path, database)
    assert rows(build(tmp_path, database), "SELECT count(*) FROM node") == [(1,)]
