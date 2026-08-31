from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, RDF, SKOS, XSD

from vault.rdf import (
    TTL_NAME,
    V,
    build_graph,
    doc_iri,
    doc_path,
    edge_triples,
    folder_iri,
    folder_triples,
    node_triples,
    section_iri,
    section_path,
    tag_iri,
    tag_triples,
)

NOTE = "---\ntype: concept\nsummary: ok\ncreated: 2026-08-10\n---\n본문\n"


def facts(relative, text):
    """Predicate -> object, for a note that holds no items.

    Folding the triples drops the subject, which is safe only while the
    subject is the document itself. Since Phase 15 that holds for a note
    with no numbered items; `test_a_subject_is_the_document_or_one_of_its
    _own_sections` is what guards the general case.
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
    assert triples[RDF.type] == V.ConceptDocument


def test_a_summary_becomes_a_literal():
    triples = facts("CIDR.md", NOTE)
    assert triples[DCTERMS.abstract] == Literal("ok")


def test_a_date_declares_its_type():
    triples = facts("CIDR.md", NOTE)
    assert triples[DCTERMS.created] == Literal("2026-08-10", datatype=XSD.date)


def test_a_missing_field_makes_no_triple():
    bare = "---\ntype: log\ncreated: 2026-08-10\n---\n본문\n"
    assert DCTERMS.abstract not in facts("a.md", bare)


def test_a_note_with_no_items_states_only_itself():
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
        (str(DCTERMS.isPartOf), str(folder_iri("200 Dev/Network")))
    ]


def test_a_note_at_the_root_is_part_of_nothing():
    assert edges("CIDR.md", NOTE) == []


def test_an_edge_from_a_note_with_no_items_leaves_the_note():
    text = with_field("builds_on", "CIDR", body="[[CIDR]] 참조")
    subjects = {s for s, _, _ in edge_triples("a.md", text, RESOLVE)}
    assert subjects == {doc_iri("a.md")}


def test_a_folder_is_part_of_the_folder_above_it():
    assert sorted(
        str(o) for _, p, o in folder_triples("200 Dev/Network") if p == DCTERMS.isPartOf
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
    tagged = [o for _, p, o in node_triples("a.md", TAGGED) if p == DCTERMS.subject]
    assert tagged == [tag_iri("Stack/Python"), tag_iri("Log")]


def test_a_note_without_tags_says_nothing():
    assert DCTERMS.subject not in facts("a.md", NOTE)


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


def make(root, files):
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


SMALL = {
    "200 Dev/Network/Network.md": NOTE,
    "200 Dev/Network/CIDR.md": (
        "---\ntype: concept\ntags:\n  - Stack/Python\n"
        "summary: ok\ncreated: 2026-08-10\n---\n[[Network]] 참조\n"
    ),
    "900 Archive/옛것.md": NOTE,
}


def test_a_note_becomes_triples(tmp_path):
    g = build_graph(make(tmp_path, SMALL))
    assert (doc_iri("200 Dev/Network/CIDR.md"), DCTERMS.abstract, Literal("ok")) in g


def test_a_folder_appears_as_a_resource(tmp_path):
    g = build_graph(make(tmp_path, SMALL))
    assert (folder_iri("200 Dev/Network"), DCTERMS.isPartOf, folder_iri("200 Dev")) in g
    assert (
        folder_iri("200 Dev/Network"),
        V.hub,
        doc_iri("200 Dev/Network/Network.md"),
    ) in g


def test_a_tag_hierarchy_is_stated(tmp_path):
    g = build_graph(make(tmp_path, SMALL))
    assert (tag_iri("Stack/Python"), SKOS.broader, tag_iri("Stack")) in g


def test_an_excluded_zone_leaves_no_trace(tmp_path):
    g = build_graph(make(tmp_path, SMALL))
    assert (doc_iri("900 Archive/옛것.md"), None, None) not in g


def test_a_link_into_an_excluded_zone_is_raw(tmp_path):
    files = dict(SMALL)
    files["200 Dev/a.md"] = NOTE.replace("본문", "[[옛것]] 참조")
    g = build_graph(make(tmp_path, files))
    assert (doc_iri("200 Dev/a.md"), V.links_to_raw, Literal("옛것")) in g


def test_the_folder_chain_is_walkable(tmp_path):
    g = build_graph(make(tmp_path, SMALL))
    rows = g.query(
        "SELECT ?f WHERE { ?d dcterms:isPartOf/dcterms:isPartOf* ?f }",
        initNs={"dcterms": DCTERMS},
        initBindings={"d": doc_iri("200 Dev/Network/CIDR.md")},
    )
    assert {str(r[0]) for r in rows} == {
        str(folder_iri("200 Dev/Network")),
        str(folder_iri("200 Dev")),
    }


def test_the_turtle_reads_back_to_the_same_graph(tmp_path):
    original = build_graph(make(tmp_path, SMALL))
    out = tmp_path / TTL_NAME
    original.serialize(destination=out, format="turtle")
    assert Graph().parse(out, format="turtle").isomorphic(original)


def test_the_iri_goes_back_to_a_path():
    assert doc_path(doc_iri("200 Dev/한글 노트.md")) == "200 Dev/한글 노트.md"


def test_a_percent_survives_the_round_trip():
    assert doc_path(doc_iri("100% 확실.md")) == "100% 확실.md"


# Phase 15 Step 4. The graph is derived and thrown away, never updated in
# place. These say what that buys, because an incremental build is exactly
# where a stale edge would survive.


def test_building_twice_yields_the_same_graph(tmp_path):
    root = make(tmp_path, SMALL)
    assert build_graph(root).isomorphic(build_graph(root))


def test_the_same_build_serialises_to_the_same_bytes(tmp_path):
    root = make(tmp_path, SMALL)
    first = build_graph(root).serialize(format="turtle")
    assert build_graph(root).serialize(format="turtle") == first


def test_a_deleted_note_leaves_no_stale_edge(tmp_path):
    # The whole case for rebuilding instead of updating. `CIDR` links to
    # `Network`; deleting the target must turn a resolved edge back into
    # raw text, and an incremental pass is where it would not.
    root = make(tmp_path, SMALL)
    cidr = doc_iri("200 Dev/Network/CIDR.md")
    network = doc_iri("200 Dev/Network/Network.md")
    assert (cidr, V.links_to, network) in build_graph(root)

    (root / "200 Dev/Network/Network.md").unlink()
    after = build_graph(root)
    assert (cidr, V.links_to, network) not in after
    assert (cidr, V.links_to_raw, Literal("Network")) in after


def test_a_renamed_note_carries_its_links(tmp_path):
    root = make(tmp_path, SMALL)
    (root / "200 Dev/Network/CIDR.md").rename(root / "200 Dev/Network/CIDR 표기법.md")
    after = build_graph(root)
    assert (doc_iri("200 Dev/Network/CIDR.md"), None, None) not in after
    assert (
        doc_iri("200 Dev/Network/CIDR 표기법.md"),
        V.links_to,
        doc_iri("200 Dev/Network/Network.md"),
    ) in after


def test_the_graph_can_be_thrown_away_and_remade(tmp_path):
    root = make(tmp_path, SMALL)
    out = root / TTL_NAME
    build_graph(root).serialize(destination=out, format="turtle")
    kept = Graph().parse(out, format="turtle")

    out.unlink()
    build_graph(root).serialize(destination=out, format="turtle")
    assert Graph().parse(out, format="turtle").isomorphic(kept)


# Phase 15 Step 5. Sections enter the graph. `links_to` moves for the 40
# body links that sit under an item — a correction, not a regression.

ITEMS = (
    "---\ntype: reflection\ncreated: 2026-08-10\n---\n"
    "머리말에서 [[CIDR]]\n\n"
    "### 인사이트 1: 첫 번째 (2026-03-22)\n"
    "[[Network]] 참조\n\n"
    "### 패턴 2: 두 번째\n"
)
ITEM_FILES = {**SMALL, "500 Mind/Q1. Better/_Insights.md": ITEMS}
INSIGHT = "인사이트 1: 첫 번째 (2026-03-22)"
INSIGHTS_DOC = "500 Mind/Q1. Better/_Insights.md"


def test_a_section_hangs_off_its_document():
    assert str(section_iri(INSIGHTS_DOC, INSIGHT)).startswith(
        str(doc_iri(INSIGHTS_DOC)) + "#"
    )


def test_only_the_separator_hash_stays_raw():
    # The heading's own `#` — Obsidian's nested anchor — is escaped, so the
    # one unescaped `#` in the IRI is always the separator.
    iri = str(section_iri(INSIGHTS_DOC, "패턴 2#안쪽"))
    assert iri.count("#") == 1
    assert iri.endswith("#패턴%202%23안쪽")


def test_a_section_iri_goes_back_to_a_document_and_a_heading():
    assert section_path(section_iri(INSIGHTS_DOC, INSIGHT)) == (INSIGHTS_DOC, INSIGHT)


def test_a_nested_heading_survives_the_round_trip():
    assert section_path(section_iri(INSIGHTS_DOC, "패턴 2#안쪽"))[1] == "패턴 2#안쪽"


def test_a_document_states_the_items_it_holds(tmp_path):
    g = build_graph(make(tmp_path, ITEM_FILES))
    assert (
        doc_iri(INSIGHTS_DOC),
        DCTERMS.hasPart,
        section_iri(INSIGHTS_DOC, INSIGHT),
    ) in g


def test_a_section_is_never_typed_v_section_by_hand(tmp_path):
    # `dcterms:hasPart rdfs:range v:Section` types it, exactly as isPartOf's
    # range types folders. Asserting it here would be the duplicate Step 5
    # forbids. `v:Insight` is different — see the next test — because no
    # range can produce it.
    g = build_graph(make(tmp_path, ITEM_FILES))
    assert (section_iri(INSIGHTS_DOC, INSIGHT), RDF.type, V.Section) not in g
    assert (section_iri(INSIGHTS_DOC, "패턴 2: 두 번째"), RDF.type, V.Section) not in g


def test_an_insight_is_typed_because_it_cannot_be_inferred(tmp_path):
    # The ontology says so in as many words: a parser writes v:Insight from
    # the heading prefix. Nothing in the data implies it.
    g = build_graph(make(tmp_path, ITEM_FILES))
    assert (section_iri(INSIGHTS_DOC, INSIGHT), RDF.type, V.Insight) in g


def test_an_item_with_no_class_stays_a_bare_section(tmp_path):
    # `패턴` is the vault's most common item and no competency question
    # asks for it, so Phase 14 declared no class. A recorded hole.
    g = build_graph(make(tmp_path, ITEM_FILES))
    assert (section_iri(INSIGHTS_DOC, "패턴 2: 두 번째"), RDF.type, None) not in g


def test_a_dated_item_states_when_it_held(tmp_path):
    g = build_graph(make(tmp_path, ITEM_FILES))
    assert (
        section_iri(INSIGHTS_DOC, INSIGHT),
        V.as_of,
        Literal("2026-03-22", datatype=XSD.date),
    ) in g


def test_a_link_under_an_item_leaves_the_item(tmp_path):
    g = build_graph(make(tmp_path, ITEM_FILES))
    network = doc_iri("200 Dev/Network/Network.md")
    assert (section_iri(INSIGHTS_DOC, INSIGHT), V.links_to, network) in g
    assert (doc_iri(INSIGHTS_DOC), V.links_to, network) not in g


def test_a_link_above_every_item_still_leaves_the_document(tmp_path):
    g = build_graph(make(tmp_path, ITEM_FILES))
    assert (doc_iri(INSIGHTS_DOC), V.links_to, doc_iri("200 Dev/Network/CIDR.md")) in g


def test_a_subquestion_document_is_a_question(tmp_path):
    # The vault keeps `type: reflection` and the builder reads the question
    # off the path — a fact you can derive is not written down twice.
    files = {**SMALL, "500 Mind/Q1. Better/By Subquestion/무엇인가.md": NOTE}
    g = build_graph(make(tmp_path, files))
    subject = doc_iri("500 Mind/Q1. Better/By Subquestion/무엇인가.md")
    assert (subject, RDF.type, V.Question) in g
    assert (subject, RDF.type, V.ConceptDocument) in g


def test_a_document_outside_by_subquestion_is_not_a_question(tmp_path):
    g = build_graph(make(tmp_path, ITEM_FILES))
    assert (doc_iri(INSIGHTS_DOC), RDF.type, V.Question) not in g


def test_a_subject_is_the_document_or_one_of_its_own_sections():
    # The invariant Phase 15 replaced "every subject is the document" with.
    # A section subject must belong to the very document being read, or the
    # builder is writing facts about a file it did not open.
    subjects = set()
    for triples in (
        node_triples(INSIGHTS_DOC, ITEMS),
        edge_triples(INSIGHTS_DOC, ITEMS, RESOLVE),
    ):
        subjects |= {s for s, _, _ in triples}
    assert subjects - {doc_iri(INSIGHTS_DOC)}
    for subject in subjects:
        assert section_path(subject)[0] == INSIGHTS_DOC
