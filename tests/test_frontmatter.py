from vault.frontmatter import fm_get, fm_list, split_frontmatter


def test_splits_frontmatter_from_body():
    text = "---\ntype: concept\n---\n# Title\nbody\n"
    fm, body = split_frontmatter(text)
    assert fm == "type: concept"
    assert body == "# Title\nbody\n"


def test_returns_none_when_document_has_no_frontmatter():
    text = "# Title\nbody\n"
    fm, body = split_frontmatter(text)
    assert fm is None
    assert body == text


def test_stops_at_the_first_closing_delimiter():
    text = "---\ntype: concept\n---\n# Title\n\n---\n\nafter the rule\n"
    fm, body = split_frontmatter(text)
    assert fm == "type: concept"
    assert "after the rule" in body


def test_ignores_a_delimiter_that_is_not_at_the_start():
    text = "# Title\n\n---\ntype: concept\n---\n"
    fm, body = split_frontmatter(text)
    assert fm is None
    assert body == text


SAMPLE = (
    "type: concept\n"
    "tags:\n"
    "  - Stack/Python\n"
    'summary: "How CIDR works"\n'
    "created: 2026-08-10"
)


def test_reads_a_scalar_field():
    assert fm_get(SAMPLE, "type") == "concept"
    assert fm_get(SAMPLE, "created") == "2026-08-10"


def test_returns_none_for_a_missing_field():
    assert fm_get(SAMPLE, "supersedes") is None


def test_strips_surrounding_quotes():
    assert fm_get(SAMPLE, "summary") == "How CIDR works"


def test_keeps_a_colon_inside_the_vaule():
    fm = "summary: Docker: what it actually is"
    assert fm_get(fm, "summary") == "Docker: what it actually is"


def test_ignores_a_key_that_appears_mid_line():
    fm = "summary: read type: below first\ntype: concept"
    assert fm_get(fm, "type") == "concept"


def test_an_empty_value_does_not_swallow_the_next_line():
    fm = "summary:\ncreated: 2026-08-10"
    assert fm_get(fm, "summary") is None


LIST_FM = (
    "type: concept\n"
    "builds_on:\n"
    '  - "[[CIDR]]"\n'
    '  - "[[Subnet mask]]"\n'
    "created: 2026-08-10"
)


def test_reads_every_item_of_a_list_block():
    assert fm_list(LIST_FM, "builds_on") == ["CIDR", "Subnet mask"]


def test_returns_an_empty_list_for_a_missing_key():
    assert fm_list(LIST_FM, "supersedes") == []


def test_stops_at_the_next_key():
    fm = 'builds_on:\n - "[[CIDR]]"\ntags:\n - Stack/Python'
    assert fm_list(fm, "builds_on") == ["CIDR"]


def test_keeps_a_plain_item_that_is_not_a_wikilink():
    fm = "tags:\n - Stack/Python\n - Topic/Network"
    assert fm_list(fm, "tags") == ["Stack/Python", "Topic/Network"]


def test_an_inline_scalar_is_not_a_list():
    assert fm_list("builds_on: [[CIDR]]", "builds_on") == []
