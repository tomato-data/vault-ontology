from vault.sections import (
    item_date,
    item_headings,
    iter_links_by_item,
    resolve_anchor,
)

# A real one, shortened. `_Insights.md` in 500 holds 24 of these.
INSIGHTS = """\
머리말이다. [[문서 밖]]

### 인사이트 1: 첫 번째
> → 상세: [[첫 문서]]

### 인사이트 2: 두 번째

### 인사이트 3: 세 번째
[[세 번째 문서]]
"""


def test_three_numbered_items_make_a_carrier():
    assert item_headings(INSIGHTS) == [
        "인사이트 1: 첫 번째",
        "인사이트 2: 두 번째",
        "인사이트 3: 세 번째",
    ]


def test_two_items_are_below_the_threshold():
    # Phase 13 measured the rule: three numbered item headings of one
    # prefix is what says a document is addressed item by item. Two is a
    # document that happens to number two paragraphs.
    body = "### 인사이트 1: 하나\n\n### 인사이트 2: 둘\n"
    assert item_headings(body) == []


def test_a_carrier_pulls_in_its_other_numbered_items():
    # Once a document is addressed item by item, every numbered item in it
    # is addressable — the threshold decides the DOCUMENT, not the heading.
    body = (
        "### 인사이트 1: 하나\n### 인사이트 2: 둘\n### 인사이트 3: 셋\n### 패턴 1: 넷\n"
    )
    assert item_headings(body)[-1] == "패턴 1: 넷"


def test_an_unnumbered_heading_is_not_an_item():
    body = "### 인사이트 1: 하나\n### 인사이트 2: 둘\n### 인사이트 3: 셋\n### 마치며\n"
    assert "마치며" not in item_headings(body)


def test_a_heading_inside_a_fence_is_not_a_heading():
    body = "```\n### 인사이트 1: 하나\n### 인사이트 2: 둘\n### 인사이트 3: 셋\n```\n"
    assert item_headings(body) == []


def test_an_anchor_matches_the_whole_heading():
    headings = ["인사이트 3: TDD 자동화 = 학습 효율"]
    assert resolve_anchor(headings, "인사이트 3: TDD 자동화 = 학습 효율") == headings[0]


def test_an_anchor_matches_the_part_before_the_first_colon():
    # How the vault actually writes it: the heading carries a title, the
    # link carries only the number.
    headings = ["인사이트 3: TDD 자동화 = 학습 효율"]
    assert resolve_anchor(headings, "인사이트 3") == headings[0]


def test_item_one_does_not_catch_item_ten():
    # The whole reason this is exact match and not prefix match. A prefix
    # rule sends `인사이트 1` to `인사이트 10` and the fact lands on the
    # wrong belief.
    headings = ["인사이트 10: 열 번째"]
    assert resolve_anchor(headings, "인사이트 1") is None


def test_an_anchor_that_names_nothing_does_not_resolve():
    assert resolve_anchor(["인사이트 1: 하나"], "인사이트 9") is None


def test_a_link_under_an_item_belongs_to_it():
    found = {document: item for item, document, _ in iter_links_by_item(INSIGHTS)}
    assert found["첫 문서"] == "인사이트 1: 첫 번째"
    assert found["세 번째 문서"] == "인사이트 3: 세 번째"


def test_a_link_above_the_first_item_belongs_to_the_document():
    found = {document: item for item, document, _ in iter_links_by_item(INSIGHTS)}
    assert found["문서 밖"] is None


def test_the_target_heading_survives_so_the_caller_can_place_it():
    body = "## 제목\n[[다른 문서#인사이트 2|별칭]]\n"
    assert list(iter_links_by_item(body)) == [(None, "다른 문서", "인사이트 2")]


def test_a_deeper_heading_stays_inside_the_item():
    body = (
        "### 인사이트 1: 하나\n### 인사이트 2: 둘\n### 인사이트 3: 셋\n"
        "#### 근거\n[[안쪽]]\n"
    )
    assert list(iter_links_by_item(body)) == [("인사이트 3: 셋", "안쪽", "")]


def test_a_heading_at_the_same_level_ends_the_item():
    body = (
        "### 인사이트 1: 하나\n### 인사이트 2: 둘\n### 인사이트 3: 셋\n"
        "### 마치며\n[[바깥]]\n"
    )
    assert list(iter_links_by_item(body)) == [(None, "바깥", "")]


def test_a_document_with_no_items_attributes_nothing():
    assert list(iter_links_by_item("## 제목\n[[어딘가]]\n")) == [(None, "어딘가", "")]


def test_a_link_in_code_is_not_a_link():
    body = "### 인사이트 1: 하나\n### 인사이트 2: 둘\n### 인사이트 3: 셋\n`[[코드]]`\n"
    assert list(iter_links_by_item(body)) == []


def test_a_same_document_anchor_names_no_other_node():
    body = "## 제목\n[[#제목]]\n"
    assert list(iter_links_by_item(body)) == []


# The date an item states for itself. 74 of the vault's 292 items carry one,
# and C08 — how a belief changed and when — is what asks for it.


def test_a_trailing_date_is_the_items_own():
    assert item_date("인사이트 20: 죽음관과 단기적 행복 (2026-03-22)") == "2026-03-22"


def test_a_date_followed_by_more_inside_the_parentheses():
    assert item_date("패턴 7: 제안-only (2026-07-14 · 자동 분류 #7)") == "2026-07-14"


def test_a_range_is_dated_by_where_it_started():
    assert (
        item_date("사례 3 — 테스트 사이클 (2026-04-29 ~ 04-30): raw 보존")
        == "2026-04-29"
    )


def test_an_item_may_state_no_date():
    assert item_date("인사이트 1: 첫 번째") is None


def test_a_date_outside_parentheses_is_not_the_items_date():
    # Measured 2026-08-31: all 74 dated items write it in parentheses, and
    # none writes it bare. Requiring the bracket keeps a date that belongs
    # to the TITLE — a retrospective on 2026-05, say — out of `as_of`.
    assert item_date("패턴 3: 2026-05 회고에서 나온 것") is None


def test_the_first_date_wins():
    assert item_date("사례 2 (2026-01-01): 2026-02-02 까지 이어짐") == "2026-01-01"
