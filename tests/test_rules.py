"""Phase 17. Rules over the asserted graph, and the fixtures Step 5 demands.

Every rule is a walk, so the tests are graphs of three or four documents.
The negation cases at the bottom are the point of the phase: an operating
judgement has to disappear when its ground does, and OWL cannot do that.
"""

from rdflib import Graph

from vault.rdf import V, doc_iri, section_iri
from vault.rules import (
    coverage,
    explain,
    genealogy,
    impact,
    invalidated,
    shared_ground,
)

A, B, C, D = (doc_iri(f"200 Dev/{name}.md") for name in "ABCD")


def graph(*triples):
    g = Graph()
    for triple in triples:
        g.add(triple)
    return g


# ── genealogy ───────────────────────────────────────────────────────
# Six of the vault's seven two-hop chains are `Decision -> Trade-offs ->
# 출처`, which is C02 word for word.


def test_a_document_with_no_ground_has_no_chain():
    assert genealogy(graph((A, V.derived_from, B)), B) == []


def test_one_hop_is_a_chain():
    g = graph((A, V.derived_from, B))
    assert genealogy(g, A) == [[(A, V.derived_from, B)]]


def test_two_hops_come_back_as_one_path():
    # `Decision -> Trade-offs -> 벤치마크`. The middle document is the
    # part a one-hop query loses, and the part C02 asks for by name.
    g = graph((A, V.derived_from, B), (B, V.derived_from, C))
    assert genealogy(g, A) == [[(A, V.derived_from, B), (B, V.derived_from, C)]]


def test_a_fork_yields_both_chains():
    g = graph((A, V.derived_from, B), (B, V.derived_from, C), (B, V.derived_from, D))
    assert len(genealogy(g, A)) == 2


def test_longest_first():
    g = graph((A, V.derived_from, B), (A, V.applies, C), (B, V.derived_from, D))
    assert [len(path) for path in genealogy(g, A)] == [2, 1]


def test_relations_of_different_kinds_chain_together():
    # A personal value informing a technical decision is C09, and it runs
    # through two different predicates.
    g = graph((A, V.expresses, B), (B, V.informed_by, C))
    assert len(genealogy(g, A)[0]) == 2


def test_builds_on_is_not_a_ground():
    # `builds_on` says one writing stands on another — a reading order.
    # Letting it in would dress that up as a chain of reasons.
    assert genealogy(graph((A, V.builds_on, B)), A) == []


def test_a_cycle_stops_instead_of_raising():
    # `contradicts` is symmetric, so two documents disagreeing is a legal
    # two-cycle and not a fault.
    g = graph((A, V.contradicts, B), (B, V.contradicts, A))
    assert genealogy(g, A) == [[(A, V.contradicts, B)]]


def test_a_section_can_stand_at_either_end():
    insight = section_iri("500 Mind/_Insights.md", "인사이트 1: 하나")
    g = graph((A, V.expresses, insight), (insight, V.derived_from, B))
    assert len(genealogy(g, A)[0]) == 2


# ── explanation ─────────────────────────────────────────────────────
# Step 3: a result that cannot be walked back is not an answer.


def test_every_hop_names_a_file():
    g = graph((A, V.derived_from, B), (B, V.derived_from, C))
    lines = explain(genealogy(g, A)[0])
    assert lines == [
        "200 Dev/A.md  --derived_from-->  200 Dev/B.md",
        "200 Dev/B.md  --derived_from-->  200 Dev/C.md",
    ]


def test_a_section_hop_names_its_heading():
    insight = section_iri("500 Mind/_Insights.md", "인사이트 1: 하나")
    line = explain([(A, V.expresses, insight)])[0]
    assert line.endswith("500 Mind/_Insights.md#인사이트 1: 하나")


# ── impact ──────────────────────────────────────────────────────────


def test_impact_finds_what_leans_on_a_document():
    # Grouped by relation, so the answer reads "applied by …, derived
    # from by …" rather than as an undifferentiated pile.
    g = graph((A, V.applies, C), (B, V.derived_from, C))
    assert impact(g, C) == [(A, V.applies), (B, V.derived_from)]


def test_impact_does_not_walk_further_back():
    # "What breaks if I change this" is about the neighbours. Two hops
    # back answers a different question and buries the first answer.
    g = graph((A, V.derived_from, B), (B, V.derived_from, C))
    assert impact(g, C) == [(B, V.derived_from)]


def test_a_document_nothing_leans_on_has_no_impact():
    assert impact(graph((A, V.derived_from, B)), A) == []


# ── shared ground ───────────────────────────────────────────────────


def test_two_documents_on_one_source_are_grouped():
    g = graph((A, V.derived_from, C), (B, V.derived_from, C))
    assert shared_ground(g) == [(C, [A, B])]


def test_one_document_on_a_source_is_not_a_group():
    assert shared_ground(graph((A, V.derived_from, C))) == []


def test_the_group_does_not_care_which_relation_was_used():
    # Two documents can reach one event by different routes and still be
    # standing on the same thing — which is what C06 wants to see.
    g = graph((A, V.derived_from, C), (B, V.applies, C))
    assert shared_ground(g) == [(C, [A, B])]


# ── invalidation ────────────────────────────────────────────────────
# Returns nothing in the vault today. Kept because the rule is right and
# the data is thin, which is not the same as a rule that asks wrongly.


def test_a_ground_that_is_contradicted_surfaces():
    g = graph((A, V.derived_from, B), (B, V.contradicts, C))
    assert invalidated(g) == [(A, B, C)]


def test_the_symmetric_direction_counts_too():
    # `contradicts` is written once and holds both ways, so the rule has
    # to look in both directions or it answers for half the vault.
    g = graph((A, V.derived_from, B), (C, V.contradicts, B))
    assert invalidated(g) == [(A, B, C)]


def test_nothing_is_invalidated_without_a_contradiction():
    assert invalidated(graph((A, V.derived_from, B))) == []


# ── Step 5: negation, retraction, time ──────────────────────────────
# The phase's whole difficulty. OWL is monotone — adding facts only adds
# conclusions — and an operating judgement has to be able to disappear.


def test_restoring_a_ground_removes_the_finding():
    # "근거가 나중에 복구됨". The contradiction is withdrawn and the
    # judgement has to go with it, not linger as a materialised warning.
    g = graph((A, V.derived_from, B), (B, V.contradicts, C))
    assert invalidated(g)
    g.remove((B, V.contradicts, C))
    assert invalidated(g) == []


def test_retracting_a_link_shortens_the_chain():
    g = graph((A, V.derived_from, B), (B, V.derived_from, C))
    assert len(genealogy(g, A)[0]) == 2
    g.remove((B, V.derived_from, C))
    assert genealogy(g, A) == [[(A, V.derived_from, B)]]


def test_running_a_rule_twice_gives_the_same_answer():
    g = graph((A, V.derived_from, B), (B, V.derived_from, C), (A, V.applies, D))
    assert genealogy(g, A) == genealogy(g, A)
    assert shared_ground(g) == shared_ground(g)


def test_a_superseded_document_still_grounds_what_named_it():
    # `supersedes` replaces a WRITING. It says nothing about whether the
    # reasoning that leaned on it still holds, and quietly dropping the
    # chain would decide that for the author.
    g = graph((A, V.derived_from, B), (C, V.derived_from, B))
    g.add((C, V.derived_from, B))
    assert len(genealogy(g, A)) == 1


def test_no_result_is_stored_anywhere():
    # The graph is input only. If a rule wrote its answer back, a retracted
    # ground would leave a stale conclusion — Phase 9's finding about
    # materialised inference, in the operating layer.
    g = graph((A, V.derived_from, B), (B, V.contradicts, C))
    before = len(g)
    genealogy(g, A)
    invalidated(g)
    shared_ground(g)
    assert len(g) == before


# ── coverage ────────────────────────────────────────────────────────


def test_coverage_counts_what_each_rule_can_answer():
    g = graph((A, V.derived_from, B), (B, V.derived_from, C), (D, V.derived_from, B))
    counts = coverage(g)
    assert counts["genealogy"] == {1: 1, 2: 2}
    assert counts["shared_ground"] == 1
    assert counts["invalidated"] == 0
