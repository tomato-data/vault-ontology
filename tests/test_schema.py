from vault.schema import find_body_tags, validate


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


def test_a_tag_at_the_start_of_a_line_is_found():
    assert find_body_tags("#Stack/Python 를 쓴다") == ["Stack/Python"]


def test_a_hex_colour_becomes_a_tag():
    assert find_body_tags("배경은 #6B4E8C 이다") == ["6B4E8C"]


def test_plain_text_holds_no_tag():
    assert find_body_tags("그냥 문장이다") == []


def test_a_markdown_anchor_is_not_a_tag():
    assert find_body_tags("[EC2](#ec2-elastic-compute) 참고") == []


def test_a_url_fragment_is_not_a_tag():
    assert find_body_tags("https://example.com/a#_oidc 문서") == []


def test_an_escaped_hash_is_not_a_tag():
    assert find_body_tags(r"PR \#5450 을 보라") == []


def test_a_number_alone_is_not_a_tag():
    assert find_body_tags("이슈 #729651 확인") == []


def test_a_heading_anchor_in_a_wikilink_is_not_a_tag():
    assert find_body_tags("[[Docker#설치]] 를 먼저") == []


def test_a_hash_inside_a_word_is_not_a_tag():
    assert find_body_tags("C#/FNA 로 만들었다") == []


def test_a_heading_is_not_a_tag():
    assert find_body_tags("# 제목\n## 부제목") == []


def test_a_tag_inside_code_is_not_a_tag():
    assert find_body_tags("`#Stack/Python` 이라고 쓴다") == []
    assert find_body_tags("```\n#Stack/Python\n```") == []
