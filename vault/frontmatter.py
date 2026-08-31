"""Parse the YAML-ish frontmatter block at the top of a vault document."""

import re
import textwrap

# `---` on its own line opens the block, the next `---` closes it.
# `re.S` lets `.` cross newlines; `*?` stops at the FIRST closing delimiter.
FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n?", re.S)


def split_frontmatter(text):
    """Return (frontmatter, body). Frontmatter is None when there is none."""
    m = FRONTMATTER.match(text)
    if not m:
        return None, text
    return m.group(1), text[m.end() :]


def fm_get(fm, key):
    """Return the scalar value of `key`, or None when absent or empty."""
    if not fm:
        return None
    # `[ \t]*` — NOT `\s*`. `\s` matches newlines, so an empty value
    # would run past the line end and read the next field as its value.
    m = re.search(rf"^{re.escape(key)}:[ \t]*(.+)$", fm, re.M)
    if not m:
        return None
    return m.group(1).strip().strip("\"'")


def fm_list(fm, key):
    """Return every item of the list block under `key`, or [] when absent."""
    if not fm:
        return []
    # `:[ \t]*\n` — the key line must END right after the colon.
    # `key: [[X]]` is an inline value, and vault never writes lists that way.
    # `(?:[ \t]+-[ \t].*\n?)+` — indented bullet lines. The next key sits at
    # column 0, so the block ends by itself. `\n?` — the last line may have none.
    m = re.search(rf"^{re.escape(key)}:[ \t]*\n((?:[ \t]+-[ \t].*\n?)+)", fm, re.M)
    if not m:
        return []
    items = []
    for line in m.group(1).splitlines():
        # The block pattern already proved a `-` is there. Drop it, then peel
        # the quotes and the wikilink brackets down to the bare name.
        item = line.strip()[1:].strip().strip("\"'")
        if item.startswith("[[") and item.endswith("]]"):
            item = item[2:-2]
        items.append(item)
    return items


def fm_block(fm, key):
    """Return {sub_key: [items]} for the indented block under `key`, or {}.

    This is how a proposal is read. Phase 12's contract puts unapproved
    facts one level in and makes approval the act of moving a line to
    column 0 — so the indentation is not decoration, it IS the state.

    `fm_list` above cannot see in here: its `^` anchors at column 0. That
    is the boundary, and it holds by construction rather than by a check,
    which is why `tests/test_frontmatter.py` states it out loud.

    The block is dedented and handed back to `fm_list`, so an item is
    peeled exactly the way an asserted one is. Two parsers would be two
    behaviours to keep in step.
    """
    if not fm:
        return {}
    # `[ \t]+.*` — every line of the block is indented, so the block ends
    # by itself at the next key. A blank line ends it too: frontmatter here
    # never holds one, and accepting it would let the block run to the end.
    m = re.search(rf"^{re.escape(key)}:[ \t]*\n((?:[ \t]+.*\n?)+)", fm, re.M)
    if not m:
        return {}
    inner = textwrap.dedent(m.group(1))
    return {sub: fm_list(inner, sub) for sub in re.findall(r"^(\w+):", inner, re.M)}
