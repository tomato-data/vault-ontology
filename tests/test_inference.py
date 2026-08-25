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


CHAIN = {
    "d/A.md": "---\ntype: concept\nbuilds_on:\n  - [[B]]\nsummary: ok\ncreated: 2026-08-10\n---\n[[B]]\n",
    "d/B.md": "---\ntype: concept\nbuilds_on:\n  - [[C]]\nsummary: ok\ncreated: 2026-08-10\n---\n본문\n",
    "d/C.md": "---\ntype: concept\nsummary: ok\ncreated: 2026-08-10\n---\n본문\n",
}


@pytest.fixture
def owl_closed(tmp_path):
    """A builds_on B builds_on C, with OWL RL - transitive + inverse fire."""
    data = build_graph(make(tmp_path, CHAIN))
    ontology = Graph().parse(ONTOLOGY, format="turtle")
    return close(data, ontology, owl=True)


def test_transitive_builds_the_far_edge(owl_closed):
    # Nobody wrote A builds_on C. Transitivity materialises it.
    assert (doc_iri("d/A.md"), V.builds_on, doc_iri("d/C.md")) in owl_closed


def test_inverse_makes_the_backlink_a_triple(owl_closed):
    # A links to B in its body; linked_by is now stored, not queried with ^.
    assert (doc_iri("d/B.md"), V.linked_by, doc_iri("d/A.md")) in owl_closed


def test_rdfs_alone_leaves_the_far_edge_unmade(tmp_path):
    # The contrast: without owl=True, transitivity does NOT fire.
    data = build_graph(make(tmp_path, CHAIN))
    ontology = Graph().parse(ONTOLOGY, format="turtle")
    rdfs_only = close(data, ontology)  # owl=False
    assert (doc_iri("d/A.md"), V.builds_on, doc_iri("d/C.md")) not in rdfs_only


def test_a_plain_query_finds_the_far_prereq_after_closure(owl_closed):
    # Phase 7 needed builds_on+ . Materialised, a one-hop pattern finds it.
    rows = owl_closed.query(
        "SELECT ?c WHERE { ?a v:builds_on ?c }",
        initNs={"v": V},
        initBindings={"a": doc_iri("d/A.md")},
    )
    assert doc_iri("d/C.md") in {row[0] for row in rows}


def test_the_same_plain_query_misses_it_before_closure(tmp_path):
    # The contrast: on raw data, one hop only reaches B, not C.
    data = build_graph(make(tmp_path, CHAIN))
    rows = data.query(
        "SELECT ?c WHERE { ?a v:builds_on ?c }",
        initNs={"v": V},
        initBindings={"a": doc_iri("d/A.md")},
    )
    assert doc_iri("d/C.md") not in {row[0] for row in rows}
