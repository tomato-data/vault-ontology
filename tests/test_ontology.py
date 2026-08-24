"""The schema file is data too - so it is tested like data.

Phase 8 moved the schema out of code (`TYPES = {...}`) and into
`vault-ontology.ttl`. These lock the axioms a later phase relies on and
fail loudly if the Turtle stops parsing.
"""

from pathlib import Path

import pytest
from rdflib import RDF, Graph
from rdflib.namespace import DCTERMS, FOAF, OWL, RDFS, SKOS

from vault.rdf import V, build_graph

ONTOLOGY = Path(__file__).resolve().parent.parent / "vault-ontology.ttl"


@pytest.fixture(scope="module")
def onto():
    return Graph().parse(ONTOLOGY, format="turtle")


def test_the_ontology_is_valid_turtle(onto):
    assert len(onto) > 0


def test_a_type_is_a_role_subclass(onto):
    # Step 2's judgment, as an axiom: a leaf type sits under a role.
    assert (V.Concept, RDFS.subClassOf, V.Content) in onto
    assert (V.SourceNote, RDFS.subClassOf, V.Imported) in onto
    assert (V.Hub, RDFS.subClassOf, V.Structural) in onto


def test_our_relation_hangs_off_a_standard(onto):
    # builds_on stays ours, but a tool that knows dcterms:references gets it.
    assert (V.builds_on, RDFS.subPropertyOf, DCTERMS.references) in onto
    assert (V.hub, RDFS.subPropertyOf, FOAF.primaryTopic) in onto


def test_builds_on_is_declared_transitive(onto):
    # Declared, not materialised - Phase 9 is where the closure is paid for.
    assert (V.builds_on, RDF.type, OWL.TransitiveProperty) in onto


def test_a_tag_is_typed_by_range(onto):
    # dcterms:subject range skos:Concept - the axiom that will, under a
    # reasoner, make every tagged object a skos:Concept.
    assert (DCTERMS.subject, RDFS.range, SKOS.Concept) in onto


def test_schema_and_data_merge(tmp_path):
    files = {
        "200 Dev/A.md": "---\ntype: concept\nsummary: ok\ncreated: 2026-08-10\n---\n본문\n",
    }
    for relative, text in files.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    data = build_graph(tmp_path)
    merged = data + Graph().parse(ONTOLOGY, format="turtle")
    assert len(merged) == len(data) + len(Graph().parse(ONTOLOGY, format="turtle"))
