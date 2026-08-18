"""Walk the vault and index every note by its file name."""

import unicodedata
from collections import defaultdict


def nfc(text):
    """macOS stores file names decomposed; typed links are composed."""
    return unicodedata.normalize("NFC", text)


def scan_vault(root):
    """Return (relative paths, name -> paths).

    The index maps to a LIST because a name is not an identifier: several
    files can carry the same one. Collapsing them here would silently drop
    every note but the last.
    """
    paths, index = [], defaultdict(list)
    for path in root.rglob("*.md"):
        relative = path.relative_to(root)
        # `.git` `.obsidian` `.trash` `.claude` — machinery, not notes.
        if any(part.startswith(".") for part in relative.parts):
            continue
        paths.append(nfc(relative.as_posix()))
    # Sorting AFTER normalisation, not before: NFD `한글` starts at U+1112
    # and NFC at U+D55C, so the two forms sort differently. The index is
    # built from this list to inherit that one order.
    paths.sort()
    for relative in paths:
        # `removesuffix` rather than `splitext`/`.stem`: both are safe HERE,
        # because the glob guarantees a `.md`. Neither is safe on a link
        # target, which carries no extension — `splitext("No.013 stone")`
        # returns `("No", ".013 stone")`. One explicit method on both sides.
        index[relative.rsplit("/", 1)[-1].removesuffix(".md")].append(relative)
    return paths, dict(index)
