from vault.links import iter_links, link_parts, link_target, strip_code


def test_a_plain_link_is_the_target():
    assert link_target("CIDR") == "CIDR"


def test_an_alias_is_dropped():
    assert link_target("CIDR|what it is") == "CIDR"


def test_an_escaped_pipe_leaves_no_backslash():
    assert link_target(r"CIDR\|what it is") == "CIDR"


def test_a_heading_anchor_is_dropped():
    assert link_target("CIDR#Notation") == "CIDR"


def test_a_heading_and_an_alias_are_both_dropped():
    assert link_target("CIDR#Notation|see here") == "CIDR"


def test_a_block_reference_is_dropped():
    assert link_target("CIDR^a1b2c3") == "CIDR"


def test_a_path_stays_in_the_target():
    assert link_target("200 Knowledge/CIDR") == "200 Knowledge/CIDR"


def test_surrounding_space_is_trimmed():
    assert link_target("  CIDR  ") == "CIDR"


def test_a_body_that_is_only_a_separator_has_no_target():
    assert link_target("#Notation") == ""
    assert link_target("|alias") == ""


# `link_parts` keeps what `link_target` throws away. Phase 15 needs the
# heading; the other three callers (graph, lint, create) still want the
# document alone, so the old name stays and delegates.


def test_parts_of_a_plain_link_have_no_heading():
    assert link_parts("CIDR") == ("CIDR", "")


def test_parts_keep_the_heading():
    assert link_parts("CIDR#Notation") == ("CIDR", "Notation")


def test_the_alias_comes_off_before_the_heading_is_read():
    assert link_parts("CIDR#Notation|see here") == ("CIDR", "Notation")
    assert link_parts(r"CIDR#Notation\|see here") == ("CIDR", "Notation")


def test_a_nested_heading_stays_whole():
    # Obsidian addresses a subheading as `#outer#inner`. Cutting at the
    # second `#` would name the wrong section, so the remainder is kept
    # as written and matched as one string.
    assert link_parts("Async#2. 체이닝#순차 vs 병렬") == ("Async", "2. 체이닝#순차 vs 병렬")


def test_a_block_reference_yields_no_heading():
    # Measured 2026-08-31: the vault holds zero `^` references, so this
    # records that they parse to nothing rather than to a section.
    assert link_parts("CIDR^a1b2c3") == ("CIDR", "")


def test_parts_of_a_same_document_anchor_have_no_document():
    assert link_parts("#Notation") == ("", "Notation")


def test_keeps_text_that_is_not_code():
    assert strip_code("plain [[CIDR]] text") == "plain [[CIDR]] text"


def test_a_fenced_block_keeps_the_line_count():
    text = "before\n```\n[[CIDR]]\n```\nafter"
    assert strip_code(text).splitlines() == ["before", "", "", "", "after"]


def test_a_language_tag_does_not_break_the_fence():
    assert "[[CIDR]]" not in strip_code("```python\n[[CIDR]]\n```")


def test_a_tilde_fence_works_the_same():
    assert "[[CIDR]]" not in strip_code("~~~\n[[CIDR]]\n~~~")


def test_two_fenced_blocks_do_not_swallow_the_text_between_them():
    text = "```\ncode\n```\n[[CIDR]]\n```\nmore\n```"
    assert "[[CIDR]]" in strip_code(text)


def test_an_unclosed_fence_runs_to_the_end():
    assert "[[CIDR]]" not in strip_code("before\n```\n[[CIDR]]\nno close")


def test_inline_code_is_removed():
    assert "[[CIDR]]" not in strip_code("see `[[CIDR]]` here")


def test_inline_code_does_not_eat_the_rest_of_the_line():
    assert "[[CIDR]]" in strip_code("`code` then [[CIDR]] then `more`")


def test_yields_every_link_in_order():
    text = "see [[CIDR]] and [[Subnet mask]] here"
    assert list(iter_links(text)) == ["CIDR", "Subnet mask"]


def test_yields_nothing_when_there_are_no_links():
    assert list(iter_links("plain text")) == []


def test_an_alias_is_already_resolved():
    assert list(iter_links("[[CIDR|what it is]]")) == ["CIDR"]


def test_an_embed_is_a_link():
    assert list(iter_links("![[CIDR]]")) == ["CIDR"]


def test_an_escaped_bracket_is_not_a_link():
    assert list(iter_links(r"write \[[CIRD]] to show the syntax")) == []


def test_a_link_inside_code_is_not_a_link():
    assert list(iter_links("run `[[CIDR]]` now")) == []


def test_a_link_inside_a_fenced_block_is_not_a_link():
    assert list(iter_links("```\n[[CIDR]]\n```")) == []


def test_a_heading_only_link_has_no_target():
    assert list(iter_links("[[#Notation]]")) == []


def test_two_links_on_one_line_do_not_merge():
    assert list(iter_links("[[A]] and [[B]]")) == ["A", "B"]
