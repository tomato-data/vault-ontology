"""Phase 18. The answer contract, and the open-world distinction it carries.

Step 3 asks for structured answer objects before text snapshots, so every
test here reads the object. `render` gets two tests at the end and no more.
"""

from rdflib import Graph, Literal

from vault.ask import (
    ANSWERED,
    BROKEN,
    EXTERNAL,
    LIVED,
    SEARCHED,
    UNRECORDED,
    affected,
    crossing,
    evidence,
    lineage,
    render,
    review,
    together,
)
from vault.rdf import V, doc_iri, section_iri

DECISION = doc_iri("400 Logic Forge/Decision.md")
TRADEOFF = doc_iri("400 Logic Forge/Trade-offs.md")
SOURCE = doc_iri("600 Content/벤치마크.md")
DIARY = doc_iri("100 Private Log/2026.01.25.md")
PRINCIPLE = doc_iri("200 Dev Knowledge Base/299 Principles/원칙.md")


def graph(*triples):
    g = Graph()
    for triple in triples:
        g.add(triple)
    return g


CHAIN = graph(
    (DECISION, V.derived_from, TRADEOFF),
    (TRADEOFF, V.derived_from, SOURCE),
)


# ── nothing leaves as an rdflib term ────────────────────────────────
# Step 4. The engine is hidden by the answer's own types, not by a promise.


def test_an_answer_carries_paths_and_not_iris():
    hop = lineage(CHAIN, DECISION).paths[0][0]
    assert hop.source == "400 Logic Forge/Decision.md"
    assert hop.relation == "derived_from"
    assert hop.target == "400 Logic Forge/Trade-offs.md"
    assert all(isinstance(field, str) for field in hop)


def test_a_section_end_carries_its_heading():
    insight = section_iri("500 Mind/_Insights.md", "인사이트 1: 하나")
    hop = lineage(graph((DECISION, V.expresses, insight)), DECISION).paths[0][0]
    assert hop.target == "500 Mind/_Insights.md"
    assert hop.target_heading == "인사이트 1: 하나"


# ── lineage · evidence ──────────────────────────────────────────────


def test_lineage_returns_the_whole_chain():
    path = lineage(CHAIN, DECISION).paths[0]
    assert [hop.target for hop in path] == [
        "400 Logic Forge/Trade-offs.md",
        "600 Content/벤치마크.md",
    ]


def test_evidence_stops_at_the_first_hop():
    # "What is this resting on" is answered by the neighbour. Returning
    # the three-hop chain here buries that answer inside a longer one.
    answer = evidence(CHAIN, DECISION)
    assert [len(path) for path in answer.paths] == [1]
    assert answer.paths[0][0].target == "400 Logic Forge/Trade-offs.md"


def test_evidence_lists_every_relation_not_just_derived_from():
    g = graph((DECISION, V.derived_from, TRADEOFF), (DECISION, V.applies, PRINCIPLE))
    assert [path[0].relation for path in evidence(g, DECISION).paths] == [
        "applies",
        "derived_from",
    ]


# ── the open-world distinction ──────────────────────────────────────
# The reason this module exists rather than a bare SPARQL string.


def test_a_document_with_grounds_is_answered():
    assert evidence(CHAIN, DECISION).status == ANSWERED


def test_a_document_with_nothing_written_is_unrecorded_not_empty():
    # "아직 안 적혔다" and "없다" are different facts, and a query that
    # returns zero rows says only the first.
    answer = evidence(CHAIN, SOURCE)
    assert answer.status == UNRECORDED
    assert "없다는 뜻이 아니다" in answer.note
    assert not answer


def test_a_lived_ground_is_not_unrecorded():
    # `derived_from: experience` is an answer — it says the source is not
    # a document. Reporting it as "nothing written" loses what was said.
    g = graph((PRINCIPLE, V.derived_from, V.experience))
    answer = evidence(g, PRINCIPLE)
    assert answer.status == LIVED
    assert "겪은 일" in answer.note


def test_a_broken_link_does_not_read_as_lived():
    # Until 2026-09-01 it did. Both landed on `_raw`, so `ask` told the
    # author their broken name was a lived source — a false statement the
    # graph could not correct, because the parser had thrown the
    # difference away before the graph existed.
    g = graph((PRINCIPLE, V.derived_from_raw, Literal("없는 문서")))
    answer = evidence(g, PRINCIPLE)
    assert answer.status == BROKEN
    assert "고쳐야 한다" in answer.note


def test_a_source_outside_the_vault_says_so():
    from vault.rdf import EXTERNAL as EXTERNAL_NS

    g = graph((PRINCIPLE, V.derived_from, EXTERNAL_NS["ai-ops-skills/tdd"]))
    answer = evidence(g, PRINCIPLE)
    assert answer.status == EXTERNAL
    assert answer.paths[0][0].target == "ext:ai-ops-skills/tdd"


def test_searched_and_absent_is_its_own_answer():
    # The status Phase 18 reserved and could not reach. `source_unknown`
    # says "I looked", which is a fact; `unrecorded` says nothing at all.
    from rdflib import Literal as L

    g = graph((PRINCIPLE, V.source_unknown, L(True)))
    answer = evidence(g, PRINCIPLE)
    assert answer.status == SEARCHED
    assert "찾아봤고" in answer.note


# ── affected ────────────────────────────────────────────────────────


def test_affected_finds_what_leans_on_a_document():
    answer = affected(CHAIN, TRADEOFF)
    assert [hop.source for path in answer.paths for hop in path] == [
        "400 Logic Forge/Decision.md"
    ]


def test_nothing_leaning_on_it_is_unrecorded():
    assert affected(CHAIN, DECISION).status == UNRECORDED


# ── review ──────────────────────────────────────────────────────────


def test_review_shows_both_hops_of_the_reason():
    g = graph((PRINCIPLE, V.derived_from, SOURCE), (SOURCE, V.contradicts, TRADEOFF))
    path = review(g).paths[0]
    assert [hop.relation for hop in path] == ["derived_from", "contradicts"]


def test_an_empty_review_says_unrecorded():
    # Not "no principle rests on a refuted claim" — "no contradiction has
    # been written down where one would show".
    assert review(CHAIN).status == UNRECORDED


# ── crossing ────────────────────────────────────────────────────────


def test_a_chain_inside_one_band_does_not_cross():
    g = graph((DECISION, V.derived_from, TRADEOFF))
    assert crossing(g).paths == []


def test_a_vault_with_no_crossing_says_unrecorded():
    # Measured 2026-08-31 this is the real vault's answer: 4 personal
    # documents carry a semantic relation against 133 technical ones, and
    # not one chain joins the two. C09 and C15 have no data yet.
    assert crossing(CHAIN).status == UNRECORDED


def test_a_technical_chain_is_not_a_crossing():
    # 103 of the vault's 163 chains run 200 to 300. Counting those as
    # crossings returns 145 of 163 and filters nothing — the phase says
    # showing many connections is not the goal.
    assert crossing(CHAIN).paths == []


def test_a_chain_between_a_life_and_the_work_crosses():
    g = graph((DIARY, V.informed_by, PRINCIPLE))
    assert crossing(g).paths


def test_the_band_is_the_first_path_segment():
    g = graph((DIARY, V.informed_by, PRINCIPLE))
    hops = crossing(g).paths[0]
    assert hops[0].source.startswith("100 Private Log")
    assert hops[0].target.startswith("200 Dev Knowledge Base")


def test_crossing_is_never_similarity():
    # Two documents in different bands sharing a tag are not a crossing.
    # Only a written relation is, which is Phase 17 Step 1's rule.
    from rdflib.namespace import DCTERMS

    from vault.rdf import tag_iri

    g = graph(
        (DIARY, DCTERMS.subject, tag_iri("Stack/Python")),
        (PRINCIPLE, DCTERMS.subject, tag_iri("Stack/Python")),
    )
    assert crossing(g).paths == []


# ── together ────────────────────────────────────────────────────────


def test_two_documents_on_one_source_come_back_together():
    g = graph((DECISION, V.derived_from, SOURCE), (PRINCIPLE, V.derived_from, SOURCE))
    assert len(together(g).paths[0]) == 2


def test_one_document_on_a_source_is_not_a_group():
    assert together(CHAIN).paths == []


# ── render ──────────────────────────────────────────────────────────


def test_a_chain_renders_as_a_chain():
    # The head once, then an arrow per hop. Repeating the source on every
    # line doubled the width and a three-hop answer stopped being readable.
    assert render(lineage(CHAIN, DECISION))[:3] == [
        "  400 Logic Forge/Decision.md",
        "      --derived_from-->  400 Logic Forge/Trade-offs.md",
        "      --derived_from-->  600 Content/벤치마크.md",
    ]


def test_a_hop_on_its_own_still_reads_as_a_sentence():
    hop = lineage(CHAIN, DECISION).paths[0][0]
    assert str(hop) == (
        "400 Logic Forge/Decision.md  --derived_from-->  400 Logic Forge/Trade-offs.md"
    )


def test_an_empty_answer_renders_its_status():
    assert render(evidence(CHAIN, SOURCE)) == [
        "  (unrecorded) 아직 안 적혔다 — 없다는 뜻이 아니다"
    ]


def test_a_group_renders_from_its_source_outward():
    # `together` is not a chain. Rendering it as one reads as "A came
    # from B came from B", so the shape is carried on the answer.
    g = graph((DECISION, V.derived_from, SOURCE), (PRINCIPLE, V.derived_from, SOURCE))
    lines = render(together(g))
    assert lines[0] == "  600 Content/벤치마크.md"
    assert all(line.strip().startswith("<--") for line in lines[1:3])


def test_a_lived_ground_is_shown_and_not_only_named():
    # The status said `lived` while the paths were empty, so the answer
    # said "the source is experience" without showing where it says so.
    g = graph((PRINCIPLE, V.derived_from, V.experience))
    answer = evidence(g, PRINCIPLE)
    assert answer.paths[0][0].relation == "derived_from"
    assert answer.paths[0][0].target == "experience"
