"""Read Obsidian wikilinks out of document bodies."""


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
