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
    input. Phase 4 reports "file:line", so the numbering has to survive.

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
