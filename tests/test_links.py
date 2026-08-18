from vault.links import link_target


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
