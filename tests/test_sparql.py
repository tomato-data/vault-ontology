import pytest

from vault.graph import (
    build,
    by_tag as sql_by_tag,
    by_type as sql_by_type,
    learning_path,
)
from vault.rdf import build_graph
from vault.sparql import by_tag, by_type, prerequisites, summaries

NOTE = "---\ntype: concept\nsummary: ok\ncreated: 2026-08-10\n---\n본문\n"


def tagged(type_, tag):
    return (
        f"---\ntype: {type_}\ntags:\n  - {tag}\n"
        "summary: ok\ncreated: 2026-08-10\n---\n본문\n"
    )


SMALL = {
    "200 Dev/Network/Network.md": NOTE,
    "200 Dev/Network/CIDR.md": tagged("concept", "Stack/Python"),
    "200 Dev/Docker.md": tagged("procedure", "Stack"),
    "300 Life/Stacked.md": tagged("reference", "Stacked"),
}


@pytest.fixture
def both(tmp_path):
    """The same vault, built twice - once as SQLite, once as RDF."""
    for relative, text in SMALL.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return build(tmp_path), build_graph(tmp_path)


def test_a_type_finds_every_note_that_declares_it(both):
    _, graph = both
    assert by_type(graph, "concept") == [
        "200 Dev/Network/CIDR.md",
        "200 Dev/Network/Network.md",
    ]


def test_a_tag_reaches_what_is_nested_under_it(both):
    _, graph = both
    assert by_tag(graph, "Stack") == ["200 Dev/Docker.md", "200 Dev/Network/CIDR.md"]


def test_a_tag_stops_at_the_slash(both):
    _, graph = both
    assert "300 Life/Stacked.md" not in by_tag(graph, "Stack")


def test_the_two_engines_agree(both):
    connection, graph = both
    for type_ in ("concept", "procedure", "reference"):
        assert by_type(graph, type_) == sql_by_type(connection, type_)
    for tag in ("Stack", "Stack/Python", "Stacked"):
        assert by_tag(graph, tag) == sql_by_tag(connection, tag)


NO_SUMMARY = "---\ntype: concept\ncreated: 2026-08-10\n---\n요약 없음\n"


@pytest.fixture
def with_a_gap(tmp_path):
    """A vault where one concept has no summary at all."""
    files = {
        "a/Full.md": tagged("concept", "Stack"),
        "a/Bare.md": NO_SUMMARY,
    }
    for relative, text in files.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return build(tmp_path), build_graph(tmp_path)


def test_a_note_without_a_summary_still_appears(with_a_gap):
    _, graph = with_a_gap
    assert summaries(graph, "concept") == [
        ("a/Bare.md", None),
        ("a/Full.md", "ok"),
    ]


def test_it_matches_a_left_join(with_a_gap):
    connection, graph = with_a_gap
    rows = connection.execute(
        "SELECT path, summary FROM node WHERE type = 'concept' ORDER BY path"
    ).fetchall()
    assert summaries(graph, "concept") == [tuple(row) for row in rows]


def builds_on(name, *prereqs):
    block = "".join(f"  - [[{p}]]\n" for p in prereqs)
    head = f"builds_on:\n{block}" if prereqs else ""
    return f"---\ntype: concept\n{head}summary: ok\ncreated: 2026-08-10\n---\n본문\n"


@pytest.fixture
def a_chain(tmp_path):
    """A builds_on B builds_on C - a three-link prerequisite chain."""
    files = {
        "200 Dev/A.md": builds_on("A", "B"),
        "200 Dev/B.md": builds_on("B", "C"),
        "200 Dev/C.md": builds_on("C"),
    }
    for relative, text in files.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return build(tmp_path), build_graph(tmp_path)


def test_plus_reaches_past_the_first_step(a_chain):
    _, graph = a_chain
    assert prerequisites(graph, "200 Dev/A.md") == ["200 Dev/B.md", "200 Dev/C.md"]


def test_the_closure_matches_sqlite(a_chain):
    connection, graph = a_chain
    reachable = {row[0] for row in learning_path(connection, "200 Dev/A.md")}
    assert set(prerequisites(graph, "200 Dev/A.md")) == reachable
