from rdflib import Literal, URIRef
from rdflib.namespace import RDF, SKOS, XSD

from vault.rdf import (
    V,
    doc_iri,
    edge_triples,
    folder_iri,
    folder_triples,
    node_triples,
    tag_iri,
    tag_triples,
)

NOTE = "---\ntype: concept\nsummary: ok\ncreated: 2026-08-10\n---\n본문\n"


def facts(relative, text):
    """Predicate -> object.

    Folding the triples like this only works because the subject is always
    the document itself, which the last test in this file is there to guard.
    """
    return {p: o for _, p, o in node_triples(relative, text)}


def test_an_iri_is_built_from_the_path():
    assert doc_iri("200 Dev/CIDR.md") == URIRef(
        "https://tomato.vault/doc/200%20Dev/CIDR"
    )


def test_the_extension_is_not_part_of_the_identity():
    assert doc_iri("CIDR.md") == doc_iri("CIDR")


def test_korean_stays_readable():
    assert doc_iri("한글.md") == URIRef("https://tomato.vault/doc/한글")


def test_a_space_is_encoded():
    assert "%20" in str(doc_iri("200 Dev/CIDR.md"))


def test_a_slash_stays_a_separator():
    assert str(doc_iri("a/b.md")).endswith("/doc/a/b")


def test_a_type_becomes_a_resource_not_a_string():
    triples = facts("CIDR.md", NOTE)
    assert triples[RDF.type] == V.Concept


def test_a_summary_becomes_a_literal():
    triples = facts("CIDR.md", NOTE)
    assert triples[V.summary] == Literal("ok")


def test_a_date_declares_its_type():
    triples = facts("CIDR.md", NOTE)
    assert triples[V.created] == Literal("2026-08-10", datatype=XSD.date)


def test_a_missing_field_makes_no_triple():
    bare = "---\ntype: log\ncreated: 2026-08-10\n---\n본문\n"
    assert V.summary not in facts("a.md", bare)


def test_every_triple_shares_the_document_as_subject():
    subjects = {s for s, _, _ in node_triples("200 Dev/CIDR.md", NOTE)}
    assert subjects == {doc_iri("200 Dev/CIDR.md")}


RESOLVE = {
    "CIDR": "200 Dev/CIDR.md",
    "가상화": "그림/가상화.png",
}.get


def edges(relative, text):
    """(predicate, object) pairs, subject guarded by the last test."""
    return sorted((str(p), str(o)) for _, p, o in edge_triples(relative, text, RESOLVE))


def with_field(field, value, body="본문"):
    return (
        f'---\ntype: concept\nsummary: ok\n{field}:\n  - "[[{value}]]"\n'
        f"created: 2026-08-10\n---\n{body}\n"
    )


def test_a_resolved_builds_on_becomes_a_resource():
    assert edges("a.md", with_field("builds_on", "CIDR")) == [
        (str(V.builds_on), str(doc_iri("200 Dev/CIDR.md")))
    ]


def test_an_unresolved_builds_on_keeps_the_text_as_a_literal():
    assert edges("a.md", with_field("builds_on", "없는 문서")) == [
        (str(V.builds_on_raw), "없는 문서")
    ]


def test_supersedes_normally_lands_in_the_raw_form():
    assert edges("a.md", with_field("supersedes", "옛 문서")) == [
        (str(V.supersedes_raw), "옛 문서")
    ]


def test_a_body_link_becomes_links_to():
    assert edges("a.md", NOTE.replace("본문", "[[CIDR]] 참조")) == [
        (str(V.links_to), str(doc_iri("200 Dev/CIDR.md")))
    ]


def test_a_frontmatter_link_is_not_also_a_body_link():
    predicates = [p for p, _ in edges("a.md", with_field("builds_on", "CIDR"))]
    assert str(V.links_to) not in predicates


def test_an_attachment_is_not_an_edge():
    assert edges("a.md", NOTE.replace("본문", "![[가상화]] 그림")) == []


def test_a_note_is_part_of_its_folder():
    assert edges("200 Dev/Network/CIDR.md", NOTE) == [
        (str(V.part_of), str(folder_iri("200 Dev/Network")))
    ]


def test_a_note_at_the_root_is_part_of_nothing():
    assert edges("CIDR.md", NOTE) == []


def test_every_edge_shares_the_document_as_subject():
    text = with_field("builds_on", "CIDR", body="[[CIDR]] 참조")
    subjects = {s for s, _, _ in edge_triples("a.md", text, RESOLVE)}
    assert subjects == {doc_iri("a.md")}


def test_a_folder_is_part_of_the_folder_above_it():
    assert sorted(
        str(o) for _, p, o in folder_triples("200 Dev/Network") if p == V.part_of
    ) == [str(folder_iri("200 Dev"))]


def test_a_top_level_folder_is_part_of_nothing():
    assert [p for _, p, _ in folder_triples("200 Dev")] == []


def test_a_folder_note_becomes_the_hub():
    triples = list(folder_triples("200 Dev/Network", hub="200 Dev/Network/Network.md"))
    assert (
        folder_iri("200 Dev/Network"),
        V.hub,
        doc_iri("200 Dev/Network/Network.md"),
    ) in triples


def test_a_folder_iri_is_not_a_document_iri():
    assert folder_iri("200 Dev/Network") != doc_iri("200 Dev/Network")


TAGGED = (
    "---\ntype: concept\ntags:\n  - Stack/Python\n  - Log\n"
    "summary: ok\ncreated: 2026-08-10\n---\n본문\n"
)


def test_a_tag_becomes_a_resource():
    tagged = [o for _, p, o in node_triples("a.md", TAGGED) if p == V.tagged]
    assert tagged == [tag_iri("Stack/Python"), tag_iri("Log")]


def test_a_note_without_tags_says_nothing():
    assert V.tagged not in facts("a.md", NOTE)


def test_a_flat_tag_has_no_parent():
    assert list(tag_triples("Stack")) == []


def test_a_nested_tag_names_its_parent():
    assert list(tag_triples("Stack/Python")) == [
        (tag_iri("Stack/Python"), SKOS.broader, tag_iri("Stack"))
    ]


def test_a_deep_tag_names_every_level():
    assert list(tag_triples("Projects/E-Project/Learnings")) == [
        (
            tag_iri("Projects/E-Project/Learnings"),
            SKOS.broader,
            tag_iri("Projects/E-Project"),
        ),
        (tag_iri("Projects/E-Project"), SKOS.broader, tag_iri("Projects")),
    ]


def test_a_tag_iri_is_not_a_document_iri():
    assert tag_iri("Stack") != doc_iri("Stack")
