import pytest

from vault.graph import build, by_tag as sql_by_tag, by_type as sql_by_type
from vault.rdf import build_graph
from vault.sparql import by_tag, by_type

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
