from rdflib import Literal, URIRef
from rdflib.namespace import RDF, XSD

from vault.rdf import V, doc_iri, node_triples

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
