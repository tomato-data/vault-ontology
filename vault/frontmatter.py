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
