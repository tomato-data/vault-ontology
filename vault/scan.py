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
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        # `.git` `.obsidian` `.trash` `.claude` — machinery, not notes.
        if any(part.startswith(".") for part in relative.parts):
            continue
        paths.append(nfc(relative.as_posix()))
    paths.sort()
    for relative in paths:
        # NOT `splitext`: it would cut "No.013 stone" at the leading dot.
        index[relative.rsplit("/", 1)[-1].removesuffix(".md")].append(relative)
    return paths, dict(index)
