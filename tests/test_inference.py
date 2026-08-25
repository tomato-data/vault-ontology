from pathlib import Path

import pytest
from rdflib import RDF, Graph

from vault.inference import close
from vault.rdf import V, build_graph, doc_iri

ONTOLOGY = Path(__file__).resolve().parent.parent / "vault-ontology.ttl"

NOTE = "---\ntype: concept\nsummary: ok\ncreated: 2026-08-10\n---\n본문\n"


def make(tmp_path, files):
    for relative, text in files.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return tmp_path


@pytest.fixture
def closed(tmp_path):
    """One concept note, data + ontology, RDFS-closed."""
    data = build_graph(make(tmp_path, {"200 Dev/CIDR.md": NOTE}))
    ontology = Graph().parse(ONTOLOGY, format="turtle")
    return close(data, ontology)


def test_a_concept_is_inferred_to_be_content(closed):
    assert (doc_iri("200 Dev/CIDR.md"), RDF.type, V.Content) in closed


def test_the_chain_reaches_the_top(closed):
    # Concept ⊂ Content ⊂ Document — two hops, both materialised.
    assert (doc_iri("200 Dev/CIDR.md"), RDF.type, V.Document) in closed


def test_the_supertype_query_is_now_a_plain_match(closed):
    # No property path, no hierarchy walk: the triple is simply there.
    assert doc_iri("200 Dev/CIDR.md") in set(closed.subjects(RDF.type, V.Document))
