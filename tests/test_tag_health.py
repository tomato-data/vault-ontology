"""When the tag vocabulary may grow, and when growth is noise.

The rule of record is 「새 축을 태그로 만들지 않는다」 — an AXIS, not a
value. These fixtures say what that distinction buys.
"""

from collections import Counter

from vault.tags import (
    FREE,
    KNOWN,
    NEEDS_REASON,
    NEW_AXIS,
    axis,
    health,
    judge,
)

VOCABULARY = Counter(
    {
        "Stack/Python": 230,
        "Stack/AWS": 120,
        "Stack/Docker": 110,
        "Stack/Go": 90,
        "Person/안동혁": 24,
        "Topic/Mathematics": 74,
        "Topic/History": 1,
        "Genre/Drama": 30,
        "Genre/입문서": 1,
    }
)


def test_the_axis_is_what_comes_before_the_first_slash():
    assert axis("Stack/Python") == "Stack"
    assert axis("Projects/E-Project/Learnings") == "Projects"


# ── the gate ────────────────────────────────────────────────────────


def test_a_tag_already_in_the_vocabulary_is_known():
    verdict, reason = judge(VOCABULARY, "Stack/Python")
    assert verdict == KNOWN
    assert "230" in reason


def test_a_new_axis_is_refused():
    # The rule that stands. A new axis is a new dimension of
    # classification, and thirty hex colour tags got in that way once.
    verdict, reason = judge(VOCABULARY, "Mood/차분함")
    assert verdict == NEW_AXIS
    assert "새 축" in reason


def test_a_new_value_on_a_referential_axis_is_free():
    # `Stack/Rust` invents no category. Rust exists; the note is about it.
    assert judge(VOCABULARY, "Stack/Rust")[0] == FREE
    assert judge(VOCABULARY, "Person/김하나")[0] == FREE


def test_a_new_value_on_a_judgemental_axis_needs_a_reason():
    # `Genre/에세이` is a call somebody made, and three other words would
    # have done. That is where a vocabulary turns into a scratchpad.
    verdict, reason = judge(VOCABULARY, "Genre/에세이")
    assert verdict == NEEDS_REASON
    assert "무엇을 가르는지" in reason


def test_a_deeper_value_still_belongs_to_its_axis():
    assert judge(VOCABULARY, "Projects/새것/Learnings")[0] == NEW_AXIS
    assert judge(Counter({"Projects/A": 3}), "Projects/새것/Learnings")[0] == FREE


# ── the signals ─────────────────────────────────────────────────────


def test_a_value_that_swallowed_its_axis_is_a_split_signal():
    # Measured in the vault: `Log/Daily-Note` is 347 of 467. It stopped
    # telling anything apart inside `Log`, which is the shape `review`
    # was born from — `capture` held 1,252 of 1,258 in 600.
    rows = {row["axis"]: row for row in health(VOCABULARY)}
    assert ("split", "Topic/Mathematics 이 74/75 (99%)") in rows["Topic"]["signals"]


def test_an_axis_whose_values_share_the_load_raises_nothing():
    rows = {row["axis"]: row for row in health(VOCABULARY)}
    assert rows["Stack"]["signals"] == []


def test_a_dominant_value_on_a_referential_axis_is_not_a_fault():
    # `Person/안동혁` at 60% says you write about one person a lot.
    # Splitting it would name the same person twice.
    rows = {row["axis"]: row for row in health(Counter({"Person/A": 9, "Person/B": 1}))}
    assert rows["Person"]["signals"] == []


def test_singletons_pile_up_only_as_a_signal_on_a_judgemental_axis():
    # `Person/정준영` used once is one person, not noise. `Genre/입문서`
    # used once is somebody reaching for a word.
    vocabulary = Counter(
        {
            "Person/A": 1,
            "Person/B": 1,
            "Person/C": 2,
            "Genre/A": 1,
            "Genre/B": 1,
            "Genre/C": 2,
        }
    )
    rows = {row["axis"]: row for row in health(vocabulary)}
    assert [kind for kind, _ in rows["Person"]["signals"]] == []
    assert "scratch" in [kind for kind, _ in rows["Genre"]["signals"]]


def test_the_kind_of_each_axis_is_reported():
    rows = {row["axis"]: row for row in health(VOCABULARY)}
    assert rows["Stack"]["kind"] == "지시형"
    assert rows["Genre"]["kind"] == "판단형"


def test_spread_is_one_when_every_value_carries_the_same_load():
    rows = {row["axis"]: row for row in health(Counter({"Stack/A": 5, "Stack/B": 5}))}
    assert rows["Stack"]["spread"] == 1.0


def test_spread_falls_as_one_value_takes_over():
    even = health(Counter({"Stack/A": 5, "Stack/B": 5}))[0]["spread"]
    lopsided = health(Counter({"Stack/A": 99, "Stack/B": 1}))[0]["spread"]
    assert lopsided < even


def test_a_single_value_axis_has_no_spread_to_measure():
    assert health(Counter({"Stack/A": 5}))[0]["spread"] == 0.0


# ── the biggest number ──────────────────────────────────────────────


def test_documents_carrying_no_tag_are_the_headline():
    # 2,078 of 4,043 in the vault. The vocabulary is not overgrown, it is
    # unused — which is the opposite of the problem the freeze addressed.
    rows = health(VOCABULARY, untagged=2078, documents=4043)
    assert ("unused", "태그 없는 문서 2,078/4,043 (51%)") in rows[-1]["signals"]


def test_a_fully_tagged_vault_raises_no_unused_signal():
    rows = health(VOCABULARY, untagged=0, documents=100)
    assert rows[-1]["signals"] == []


def test_axes_with_signals_come_first():
    kinds = [len(row["signals"]) for row in health(VOCABULARY)]
    assert kinds == sorted(kinds, reverse=True)
