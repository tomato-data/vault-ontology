"""Parse the YAML-ish frontmatter block at the top of a vault document."""

import re

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
