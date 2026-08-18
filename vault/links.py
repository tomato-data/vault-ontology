"""Read Obsidian wikilinks out of document bodies."""

import re


def link_target(raw):
    r"""Return the document a `[[...]]` body points at.

    Cut at the FIRST separator. The order matters: an escaped pipe `\|` must
    go before a bare `|`, or the backslash stays glued to the target and a
    working link reads as broken.

    Cutting is safe because these characters cannot reach the target: `|` is
    banned in note names, and `#`/`^` are read as separators before anything
    else, so a note whose name holds one is unreachable by wikilink anyway.
    """
    target = raw
    for separator in ("\\|", "|", "#", "^"):
        target = target.split(separator, 1)[0]
    return target.strip()


# A fence line: three backticks or tildes, optionally with a language tag.
# Obsidian writes ```python far more often than a bare ```.
FENCE = re.compile(r"^[ \t]*(```|~~~)")

# Inline code, within one line. `[^`]*` cannot cross a backtick, so two spans
# on the same line stay two spans instead of merging into one greedy match.
INLINE = re.compile(r"`[^`]*`")


def strip_code(text):
    """Return `text` with code blanked out, line for line.

    Lines are replaced, never deleted: line N of the result is line N of the
    input. Callers report problems as `file:line`, so the numbering has to
    survive this pass.

    Fences go first. ``` contains `, so peeling inline code off first would
    eat two of the three backticks and the fence would stop being a fence.
    """
    out = []
    in_fence = False
    for line in text.split("\n"):
        if FENCE.match(line):
            in_fence = not in_fence
            out.append("")
        elif in_fence:
            out.append("")
        else:
            out.append(INLINE.sub("", line))
    return "\n".join(out)


# `[[target]]` or `![[target]]`. `(?<!\\)` — a backslash in front escapes the
# whole thing. `[^\[\]]+` — the inside holds no brackets, so two links on one
# line stay two instead of merging into one greedy match.
LINK = re.compile(r"(?<!\\)!?\[\[([^\[\]]+)\]\]")


def iter_links(text):
    """Yield the target of every wikilink in `text`, in order.

    Pass the BODY, not the whole document. `builds_on` lives in the
    frontmatter and is already an edge of its own; counting it here again
    would put the same relation in the graph twice.

    An empty target means the link points inside the current document
    (`[[#Heading]]`), so it names no other node and is dropped.
    """
    for match in LINK.finditer(strip_code(text)):
        target = link_target(match.group(1))
        if target:
            yield target
