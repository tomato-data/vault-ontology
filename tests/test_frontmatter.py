from vault.frontmatter import split_frontmatter


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
