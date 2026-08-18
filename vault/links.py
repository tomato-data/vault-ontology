"""Read Obsidian wikilinks out of document bodies."""


def link_target(raw):
    r"""Return the document a `[[...]]` body points at.

    Cut at the FIRST separator. The order matters: an escaped pipe `\|` must
    go before a bare `|`, or the backslash stays glued to the target and a
    working link reads as broken.
    """
    for separator in ("\\|", "|", "#", "^"):
        raw = raw.split(separator, 1)[0]
    return raw.strip()
