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
    # ConceptDocument ⊂ Content ⊂ Document — two hops, both materialised.
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


# ---------------------------------------------------------------------------
# Negative tests — what must NEVER be inferred.
#
# Phase 14 Step 3. A positive test says the reasoner reached the right answer;
# these say it did not reach a WRONG one. Every failure they lock was live in
# the real graph on 2026-08-26, silent, and found only by asking whether two
# roles overlapped.
# ---------------------------------------------------------------------------

ACROSS_ROLES = {
    # A concept I wrote, standing on a book I only transcribed. Ordinary.
    "200 Dev/FinOps.md": (
        "---\ntype: concept\nbuilds_on:\n  - [[KAO]]\n  - [[Hub]]\n"
        "summary: ok\ncreated: 2026-08-10\n---\n[[KAO]]\n"
    ),
    # A capture that itself builds on something. Also ordinary.
    "600 Content/KAO.md": (
        "---\ntype: capture\nbuilds_on:\n  - [[공고]]\n"
        "summary: ok\ncreated: 2026-08-10\n---\n본문\n"
    ),
    "600 Content/공고.md": "---\ntype: capture\nsummary: ok\ncreated: 2026-08-10\n---\n본문\n",
    # A hub, pointed at from a note of mine.
    "200 Dev/Hub.md": "---\ntype: hub\ncreated: 2026-08-10\n---\n[[FinOps]]\n",
}


@pytest.fixture
def roles(tmp_path):
    data = build_graph(make(tmp_path, ACROSS_ROLES))
    ontology = Graph().parse(ONTOLOGY, format="turtle")
    return close(data, ontology, owl=True)


def test_a_source_note_never_becomes_content(roles):
    """`builds_on` says nothing about who wrote either end.

    Both directions used to leak: `rdfs:range v:Content` typed the TARGET of
    builds_on as mine, and `rdfs:domain v:Content` typed the SOURCE. On the
    real vault that put 27 documents in two roles at once, so the query
    v:Content exists to answer - my own thinking, captures excluded - was
    wrong by 27 and said nothing about it.
    """
    kao = doc_iri("600 Content/KAO.md")
    assert (kao, RDF.type, V.Imported) in roles
    assert (kao, RDF.type, V.Content) not in roles


def test_the_three_roles_stay_disjoint(roles):
    content = set(roles.subjects(RDF.type, V.Content))
    imported = set(roles.subjects(RDF.type, V.Imported))
    structural = set(roles.subjects(RDF.type, V.Structural))
    assert content & imported == set()
    assert content & structural == set()
    assert imported & structural == set()


def test_nothing_reaches_document_by_inference_alone(roles):
    """Every document is typed by its own `type:`, never by a relation.

    Measured on the real vault: zero resources reached v:Document any other
    way. So a link may point at a SECTION - Phase 13's new resource, which is
    not a document - without the reasoner quietly turning it into one.
    """
    leaves = [
        V.ConceptDocument, V.ProcedureDocument, V.ReferenceDocument,
        V.PrincipleDocument, V.DecisionDocument, V.CaseDocument,
        V.LogDocument, V.ReflectionDocument, V.ProjectDocument,
        V.TradeoffDocument, V.CaptureDocument, V.HubDocument,
        V.TemplateDocument,
    ]
    declared = {s for leaf in leaves for s in roles.subjects(RDF.type, leaf)}
    assert set(roles.subjects(RDF.type, V.Document)) == declared


def test_a_section_does_not_become_a_document(tmp_path):
    """Phase 15 has no section parser yet, so this one is a guard set early.

    The ontology has to be safe for sections BEFORE they arrive, because the
    day they arrive is the day `v:links_to rdfs:range v:Document` would have
    quietly typed every one of them a document and undone Phase 13. The
    section is minted by hand here; nothing else in the codebase makes one.
    """
    from rdflib import URIRef
    from rdflib.namespace import DCTERMS

    data = build_graph(make(tmp_path, {"200 Dev/CIDR.md": NOTE}))
    doc = doc_iri("200 Dev/CIDR.md")
    section = URIRef(f"{doc}#%EC%9D%B8%EC%82%AC%EC%9D%B4%ED%8A%B8%203")
    data.add((doc, DCTERMS.hasPart, section))
    data.add((doc, V.links_to, section))

    closed = close(data, Graph().parse(ONTOLOGY, format="turtle"), owl=True)
    assert (section, RDF.type, V.Document) not in closed
    assert (section, RDF.type, V.Content) not in closed
