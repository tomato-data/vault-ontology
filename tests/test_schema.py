from vault.schema import validate


def codes(fm):
    """Just the rule names, so a test does not depend on message wording."""
    return sorted(code for code, _ in validate(fm))


GOOD = "type: concept\n" "summary: How CIDR works\n" "created: 2026-08-10"


def test_a_complete_document_has_no_violation():
    assert validate(GOOD) == []


def test_a_missing_type_is_a_violation():
    assert codes("summary: x\ncreated: 2026-08-10") == ["type missing"]


def test_a_type_outside_the_thirteen_is_a_violation():
    assert codes("type: essay\ncreated: 2026-08-10") == ["type unknown"]


def test_a_judgement_type_needs_a_summary():
    assert codes("type: concept\ncreated: 2026-08-10") == ["summary missing"]


def test_an_automatic_type_does_not_need_a_summary():
    assert validate("type: log\ncreated: 2026-08-10") == []


def test_a_summary_over_the_limit_is_a_violation():
    fm = f"type: concept\nsummary: {'x' * 81}\ncreated: 2026-08-10"
    assert codes(fm) == ["summary too long"]


def test_more_than_three_builds_on_is_a_violation():
    fm = GOOD + "\nbuilds_on:\n" + "".join(f'  - "[[Doc {n}]]"\n' for n in range(4))
    assert codes(fm) == ["builds_on too many"]


def test_a_date_that_is_only_shaped_right_is_a_violation():
    assert codes("type: log\ncreated: 2026-13-99") == ["created invalid"]


def test_a_missing_date_is_a_violation():
    assert codes("type: log") == ["created missing"]


def test_every_violation_is_reported_not_only_the_first():
    fm = f"type: essay\nsummary: {'x' * 81}\ncreated: 2026-13-99"
    assert codes(fm) == ["created invalid", "summary too long", "type unknown"]
