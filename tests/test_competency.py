"""The three competency questions that are ontology problems.

Phase 10 judged all 30. Eighteen turned out to be authoring-contract problems
- nobody writes the fact down - and only C02, C08 and C27 need the graph to
mean something. These lock that the Phase 14 vocabulary actually answers them.

The facts are hand-written. Phase 15 builds the parser that will produce them
from frontmatter and headings; until then a fixture is the only ABox there is,
and a vocabulary that cannot answer its questions on a fixture will not answer
them on the vault either.
"""

from pathlib import Path

import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, RDF, XSD

from vault.inference import close
from vault.rdf import V, doc_iri

ONTOLOGY = Path(__file__).resolve().parent.parent / "vault-ontology.ttl"

NS = {"v": V, "dcterms": DCTERMS}


def section(relative, heading):
    """A section IRI: the document's, plus a fragment. Phase 13 Step 4."""
    return URIRef(f"{doc_iri(relative)}#{heading}")


@pytest.fixture(scope="module")
def onto():
    return Graph().parse(ONTOLOGY, format="turtle")


# ---------------------------------------------------------------------------
# C02 — what tradeoff and what source lie behind this decision, and where does
#       that source stand now?
#
# The one relation `derived_from` carries all of it. That was the judgment
# behind absorbing five candidates into one: the TARGET'S OWN TYPE says what
# kind of source it was, so the relation does not need to be split.
# ---------------------------------------------------------------------------

C02_QUERY = """
SELECT ?target ?kind ?status WHERE {
  ?decision v:derived_from ?target .
  ?target a ?kind .
  OPTIONAL { ?target v:status ?status }
}
"""


@pytest.fixture
def c02(onto):
    g = Graph()
    decision = doc_iri("400 Logic Forge/Decision - Pragmatic vs Clean.md")
    tradeoff = doc_iri("400 Logic Forge/Trade-offs - Pragmatic vs Clean.md")
    source = doc_iri("600 Content/FastAPI Pragmatic vs Clean.md")
    g.add((decision, RDF.type, V.DecisionDocument))
    g.add((tradeoff, RDF.type, V.TradeoffDocument))
    g.add((source, RDF.type, V.CaptureDocument))
    g.add((decision, V.derived_from, tradeoff))
    g.add((decision, V.derived_from, source))
    g.add((source, V.status, V.archived))
    return close(g, onto, owl=True), decision, tradeoff, source


def test_c02_one_relation_still_tells_the_two_apart(c02):
    closed, _, tradeoff, source = c02
    rows = {(r[0], r[1]) for r in closed.query(C02_QUERY, initNs=NS)}
    assert (tradeoff, V.TradeoffDocument) in rows
    assert (source, V.CaptureDocument) in rows


def test_c02_the_source_carries_its_current_state(c02):
    closed, _, _, source = c02
    rows = {(r[0], r[2]) for r in closed.query(C02_QUERY, initNs=NS)}
    assert (source, V.archived) in rows


def test_c02_the_source_is_not_typed_mine(c02):
    """The negative half of the same question.

    `derived_from` points at a capture here. If it carried a range the
    way `builds_on` used to, this book note would come back as something I
    wrote - which is the 27-document fault Phase 14 Step 3 removed.
    """
    closed, _, _, source = c02
    assert (source, RDF.type, V.Imported) in closed
    assert (source, RDF.type, V.Content) not in closed


# ---------------------------------------------------------------------------
# C08 — how did this belief change over time, and what caused the change?
#
# Needs the section unit: `_Insights.md` is one document holding 24 beliefs,
# each with its own date. Document-level facts cannot express this at all.
# ---------------------------------------------------------------------------

C08_QUERY = """
SELECT ?later ?earlier ?when ?cause WHERE {
  ?later v:diverges_from ?earlier ;
         v:as_of         ?when .
  OPTIONAL { ?later v:derived_from ?cause }
}
"""

INSIGHTS = "500 Mind Compiler/Q7. Who Am I/_Insights.md"


@pytest.fixture
def c08(onto):
    g = Graph()
    doc = doc_iri(INSIGHTS)
    early = section(INSIGHTS, "인사이트 15")
    late = section(INSIGHTS, "인사이트 19")
    event = doc_iri("100 Private Log/103 Debugger/103.1 self/어떤 성찰.md")
    g.add((doc, RDF.type, V.ReflectionDocument))
    g.add((doc, DCTERMS.hasPart, early))
    g.add((doc, DCTERMS.hasPart, late))
    g.add((early, RDF.type, V.Insight))
    g.add((late, RDF.type, V.Insight))
    g.add((early, V.as_of, Literal("2026-03-16", datatype=XSD.date)))
    g.add((late, V.as_of, Literal("2026-06-05", datatype=XSD.date)))
    g.add((late, V.diverges_from, early))
    g.add((late, V.derived_from, event))
    return close(g, onto, owl=True), early, late, event


def test_c08_the_two_moments_are_separate_resources(c08):
    closed, early, late, _ = c08
    assert early != late
    assert (early, RDF.type, V.Insight) in closed
    assert (late, RDF.type, V.Insight) in closed


def test_c08_the_change_and_its_cause_come_back_together(c08):
    closed, early, late, event = c08
    rows = {(r[0], r[1], str(r[2]), r[3]) for r in closed.query(C08_QUERY, initNs=NS)}
    assert (late, early, "2026-06-05", event) in rows


def test_c08_a_section_is_typed_by_range_not_by_hand(c08):
    """`dcterms:hasPart rdfs:range v:Section` does the typing.

    Nobody wrote `a v:Section` in the fixture. This is the one place Phase 14
    Step 3 let a range survive on a new term, and it is why the reversed
    direction was worth taking over minting `v:section_of`.
    """
    closed, early, _, _ = c08
    assert (early, RDF.type, V.Section) in closed
    assert (early, RDF.type, V.Document) not in closed


# ---------------------------------------------------------------------------
# C27 — which band answers this subquestion, and which subquestions have none?
#
# The OPTIONAL is the question's real payload. An inner join would drop the
# unanswered ones, which are the interesting half.
# ---------------------------------------------------------------------------

C27_QUERY = """
SELECT ?question ?answer WHERE {
  ?question a v:Question .
  OPTIONAL { ?question v:answered_by ?answer }
}
"""


@pytest.fixture
def c27(onto):
    g = Graph()
    answered = doc_iri("500 Mind Compiler/Q6. Relationship/By Subquestion/결혼은 하고 싶은가.md")
    unanswered = doc_iri("500 Mind Compiler/Q7. Who Am I/By Subquestion/관찰자 역할을 어떻게 쓸까.md")
    evidence = doc_iri("600 Content/이동진 평론가의 인간관계 철학.md")
    g.add((answered, RDF.type, V.ReflectionDocument))
    g.add((unanswered, RDF.type, V.ReflectionDocument))
    g.add((evidence, RDF.type, V.CaptureDocument))
    g.add((answered, V.answered_by, evidence))
    g.add((unanswered, RDF.type, V.Question))  # no answer yet
    return close(g, onto, owl=True), answered, unanswered, evidence


def test_c27_writing_an_answer_is_what_makes_it_a_question(c27):
    """`v:answered_by rdfs:domain v:Question` — the one domain kept.

    Nobody typed the answered document a question. Every other domain in the
    file was deleted for inferring nothing or inferring wrongly; this one
    states something true that no other triple says.
    """
    closed, answered, _, _ = c27
    assert (answered, RDF.type, V.Question) in closed


def test_c27_a_document_can_be_a_question_without_stopping_being_a_document(c27):
    closed, answered, _, _ = c27
    assert (answered, RDF.type, V.ReflectionDocument) in closed
    assert (answered, RDF.type, V.Content) in closed


def test_c27_the_unanswered_question_still_comes_back(c27):
    closed, answered, unanswered, evidence = c27
    rows = {(r[0], r[1]) for r in closed.query(C27_QUERY, initNs=NS)}
    assert (answered, evidence) in rows
    assert (unanswered, None) in rows


def test_c27_the_evidence_document_is_not_promoted_to_a_question(c27):
    """The object of answered_by is not a question. Only the subject is."""
    closed, _, _, evidence = c27
    assert (evidence, RDF.type, V.Question) not in closed
