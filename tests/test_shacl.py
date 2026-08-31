"""Four fixtures per shape: passing, missing, wrong type, boundary.

Phase 16 Step 2. Each shape is measured against a graph built by hand, so
the fixture says exactly what the rule means and nothing else can drift in.
"""

import pytest
from rdflib import Graph, Literal
from rdflib.namespace import DCTERMS, RDF

from vault.rdf import V, doc_iri, section_iri
from vault.shacl import findings, format_finding, shapes_graph, summarise


@pytest.fixture(scope="module")
def shapes():
    return shapes_graph()


def graph(*triples):
    g = Graph()
    for triple in triples:
        g.add(triple)
    return g


def check(shapes, *triples):
    """Findings for a hand-built graph, worst first."""
    return findings(graph(*triples), shapes)[1]


A = doc_iri("200 Dev/A.md")
B = doc_iri("200 Dev/B.md")
SUMMARY = (A, DCTERMS.abstract, Literal("무엇에 대한 글인지"))


# ── v:NoSelfRelation ────────────────────────────────────────────────
# Violation. Zero in the vault, which is what lets it be strict — but two
# real ones existed on 2026-08-26, hidden behind link aliases.


def test_a_relation_to_another_document_passes(shapes):
    assert check(shapes, (A, V.derived_from, B)) == []


def test_a_relation_to_itself_is_a_violation(shapes):
    found = check(shapes, (A, V.derived_from, A))
    assert [f["severity"] for f in found] == ["violation"]
    assert "자기 자신" in found[0]["message"]


def test_the_violation_names_the_file_not_the_iri(shapes):
    assert check(shapes, (A, V.derived_from, A))[0]["path"] == "200 Dev/A.md"


def test_every_semantic_relation_is_covered_not_just_derived_from(shapes):
    for relation in (V.contradicts, V.applies, V.expresses, V.builds_on):
        assert check(shapes, (A, relation, A)), relation


def test_a_structural_link_to_itself_is_not_this_shapes_business(shapes):
    # `links_to` is body text, and a document quoting its own name is not
    # the machine-written mistake this shape exists for.
    assert check(shapes, (A, V.links_to, A)) == []


# ── v:JudgementNeedsSummary ─────────────────────────────────────────
# Violation. 22 in the vault, the same 22 Python lint reports — the one
# parity rule in this phase.


def test_a_concept_with_a_summary_passes(shapes):
    assert check(shapes, (A, RDF.type, V.ConceptDocument), SUMMARY) == []


def test_a_concept_without_a_summary_is_a_violation(shapes):
    found = check(shapes, (A, RDF.type, V.ConceptDocument))
    assert [f["severity"] for f in found] == ["violation"]
    assert "summary" in found[0]["message"]


def test_a_log_without_a_summary_passes(shapes):
    # The vault's v1.16 profile asks for a summary in the judgement band
    # only. A log records a flow, and a one-line summary of a flow is noise.
    assert check(shapes, (A, RDF.type, V.LogDocument)) == []


def test_all_four_judgement_classes_are_targeted(shapes):
    for class_ in (
        V.ConceptDocument,
        V.ProcedureDocument,
        V.ReferenceDocument,
        V.CaseDocument,
    ):
        assert check(shapes, (A, RDF.type, class_)), class_


def test_an_empty_summary_is_still_a_summary(shapes):
    # The boundary case. SHACL counts triples; whether a string says
    # anything is Python lint's `summary too long` neighbourhood, not this.
    passing = check(
        shapes, (A, RDF.type, V.ConceptDocument), (A, DCTERMS.abstract, Literal(""))
    )
    assert passing == []


# ── v:SectionBelongsToItsDocument ───────────────────────────────────
# Violation. 0 of 324. The graph-side twin of the parser invariant Phase 15
# Round 5 settled on.

OWN = section_iri("200 Dev/A.md", "인사이트 1: 하나")
OTHERS = section_iri("200 Dev/B.md", "인사이트 1: 하나")


def test_a_document_holding_its_own_section_passes(shapes):
    assert check(shapes, (A, DCTERMS.hasPart, OWN)) == []


def test_a_document_holding_another_documents_section_is_a_violation(shapes):
    found = check(shapes, (A, DCTERMS.hasPart, OTHERS))
    assert [f["severity"] for f in found] == ["violation"]


def test_a_part_that_is_a_whole_document_is_a_violation(shapes):
    # No `#` at all — a document claiming another document as a part.
    assert check(shapes, (A, DCTERMS.hasPart, B))


def test_a_prefix_match_is_not_enough(shapes):
    # `.../A` and `.../A 부록` share a prefix. Without the `#` the check
    # would pass a section of a different document whose path starts the
    # same way — the same off-by-one as `인사이트 1` versus `인사이트 10`.
    sibling = section_iri("200 Dev/A 부록.md", "인사이트 1: 하나")
    assert check(shapes, (A, DCTERMS.hasPart, sibling))


# ── v:PrincipleNeedsGround ──────────────────────────────────────────
# Warning. 59 of 94. Cannot be a Violation: refusing 63% of the principles
# would mean refusing the vault.


def test_a_principle_with_a_ground_passes(shapes):
    assert (
        check(shapes, (A, RDF.type, V.PrincipleDocument), (A, V.derived_from, B)) == []
    )


def test_a_principle_without_a_ground_is_a_warning(shapes):
    found = check(shapes, (A, RDF.type, V.PrincipleDocument))
    assert [f["severity"] for f in found] == ["warning"]


def test_experience_counts_as_a_ground(shapes):
    # `derived_from: experience` says the source is lived, not written. It
    # lands on the `_raw` predicate, and it is still an answer.
    found = check(
        shapes,
        (A, RDF.type, V.PrincipleDocument),
        (A, V.derived_from_raw, Literal("experience")),
    )
    assert [f["severity"] for f in found] == ["warning"]  # only the raw-link warning
    assert "해석되지 않았다" in found[0]["message"]


def test_a_concept_without_a_ground_is_not_asked_for_one(shapes):
    assert check(shapes, (A, RDF.type, V.ConceptDocument), SUMMARY) == []


# ── v:DecisionNeedsGround ───────────────────────────────────────────
# Warning. 40 of 46.


def test_a_decision_grounded_by_applies_passes(shapes):
    assert check(shapes, (A, RDF.type, V.DecisionDocument), (A, V.applies, B)) == []


def test_a_decision_without_a_ground_is_a_warning(shapes):
    found = check(shapes, (A, RDF.type, V.DecisionDocument))
    assert [f["severity"] for f in found] == ["warning"]


# ── v:SemanticLinkShouldResolve ─────────────────────────────────────
# Warning. 2 in the vault, both `experience`. It exists to keep the count
# visible, not to ask for a fix.


def test_a_resolved_relation_raises_nothing(shapes):
    assert check(shapes, (A, V.derived_from, B)) == []


def test_an_unresolved_relation_is_a_warning(shapes):
    found = check(shapes, (A, V.derived_from_raw, Literal("없는 문서")))
    assert [f["severity"] for f in found] == ["warning"]


def test_an_unresolved_body_link_is_not_this_shapes_business(shapes):
    # 369 broken body links live in the vault and Python lint reports them.
    # A semantic fact is the thing this phase refuses to let break.
    assert check(shapes, (A, V.links_to_raw, Literal("없는 문서"))) == []


# ── report shape ────────────────────────────────────────────────────


def test_findings_come_worst_first(shapes):
    found = check(
        shapes,
        (A, RDF.type, V.DecisionDocument),  # warning — no ground
        (B, V.derived_from, B),  # violation — points at itself
    )
    assert [f["severity"] for f in found] == ["violation", "warning"]


def test_a_finding_about_a_section_names_the_heading(shapes):
    found = check(shapes, (OWN, V.derived_from, OWN))
    assert found[0]["path"] == "200 Dev/A.md"
    assert found[0]["heading"] == "인사이트 1: 하나"


def test_a_line_leads_back_to_the_heading(shapes):
    line = format_finding(check(shapes, (OWN, V.derived_from, OWN))[0])
    assert line.startswith("200 Dev/A.md#인사이트 1: 하나: [violation]")


def test_a_clean_graph_conforms(shapes):
    conforms, found = findings(graph((A, V.derived_from, B)), shapes)
    assert conforms and found == []


def test_the_summary_counts_by_severity(shapes):
    found = check(
        shapes,
        (A, RDF.type, V.DecisionDocument),
        (B, V.derived_from, B),
    )
    severities, _ = summarise(found)
    assert severities == {"violation": 1, "warning": 1}
