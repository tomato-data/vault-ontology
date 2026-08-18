from vault.links import link_target, strip_code


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
