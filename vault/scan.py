"""Turn file names into something a link can point at.

Names are what Obsidian links with, and names are not identifiers: they
repeat, they differ by letter case, and macOS stores them decomposed
while typed links are composed. Everything here exists to survive that.
"""

import unicodedata
from collections import defaultdict


def nfc(text):
    """macOS stores file names decomposed; typed links are composed."""
    return unicodedata.normalize("NFC", text)


def scan_vault(root):
    """Return (notes, index, targets).

    Three sets, because they are three different things:

        notes    every `.md`, the documents there is text to read
        index    every FILE by name — a link can point at an attachment,
                 and `![[가상화.png]]` is a working link, not a broken one
        targets  every file's path, for the tail match in `resolve_link`

    Treating "documents" and "what a link may hit" as one set reported 582
    image embeds as broken links against the real vault.

    A name maps to a LIST because a name is not an identifier: several
    files can carry the same one. Collapsing them would silently drop
    every file but the last.
    """
    notes, targets, index = [], [], defaultdict(list)
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        # `.git` `.obsidian` `.trash` `.claude` — machinery, not the vault.
        # `.trash` especially: a link into it points at a deleted note and
        # should stay broken.
        if not path.is_file() or any(p.startswith(".") for p in relative.parts):
            continue
        targets.append(nfc(relative.as_posix()))
    # Sorting AFTER normalisation, not before: NFD `한글` starts at U+1112
    # and NFC at U+D55C, so the two forms sort differently. Both lists below
    # inherit this one order.
    targets.sort()
    for relative in targets:
        name = relative.rsplit("/", 1)[-1]
        index[name].append(relative)
        if name.endswith(".md"):
            # `removesuffix` rather than `splitext`/`.stem`: both are safe
            # HERE, but neither is safe on a link target, which carries no
            # extension — `splitext("No.013 stone")` gives `("No", ".013…")`.
            index[name.removesuffix(".md")].append(relative)
            notes.append(relative)
    return notes, dict(index), targets


def _nearest(candidates, source):
    """Prefer a candidate that sits inside the source's own folder.

    Only that. A shared zone says almost nothing — one tenth of the vault
    lives under `300 Runtime`. Measured on the real vault: this rule moves
    126 links, while "shares any prefix" moves 1,443, most onto the wrong
    file. A sibling folder is not near enough to overrule sorted order.
    """
    if source is None or len(candidates) == 1:
        return candidates[0]
    here = source.rsplit("/", 1)[0] + "/" if "/" in source else ""
    for candidate in candidates:
        if here and candidate.startswith(here):
            return candidate
    return candidates[0]


def resolve_link(target, index, paths, source=None):
    """Return the path a wikilink target points at, or None.

    A repeated name resolves to the FIRST path in sorted order. Not the
    right one — the same one. Reproducibility is what the graph needs; the
    ambiguity itself is reported separately.
    """
    target = nfc(target)
    if target in index:
        return _nearest(index[target], source)
    # Append `.md` to the target rather than stripping it from the path:
    # a target has no extension, so there is nothing here to cut wrongly.
    # BOTH sides get a leading `/` so the match lands on a directory
    # boundary. Without it, "work/Subnet mask" hits "Network/Subnet mask";
    # with it on the target alone, a full path like "500 Mind/Hub" stops
    # matching, because the vault root carries no slash in front of it.
    tail = "/" + target + ".md"
    matches = [path for path in paths if ("/" + path).endswith(tail)]
    if matches:
        return _nearest(matches, source)
    return None


def duplicate_names(index):
    """Return every name that more than one file carries."""
    return {name: paths for name, paths in index.items() if len(paths) > 1}


def case_collisions(index):
    """Return names that differ from each other only by letter case.

    Keyed by the folded form, which is a grouping key and not necessarily
    a name the vault holds. One entry per problem rather than per pair:
    three spellings of the same word are one collision, not three.
    """
    grouped = defaultdict(list)
    for name in index:
        grouped[name.casefold()].append(name)
    return {
        folded: sorted(names) for folded, names in grouped.items() if len(names) > 1
    }


def folder_note(directory, is_node):
    r"""The note standing in for `directory`, if there is one.

    Two conventions, both pinned by PATH rather than by name:

        A/B/B.md    the folder note inside the folder
        A/B.md      the folder note beside it

    Never a name lookup. The answer key resolves `B` globally and lands 139
    edges on the wrong note — a travel plan in `000 Index/Dots/` becomes
    part of `500 Mind Compiler/Q1. Better Developer/Dots.md`.
    """
    name = directory.rsplit("/", 1)[-1]
    above = directory.rsplit("/", 1)[0] + "/" if "/" in directory else ""
    for candidate in (f"{directory}/{name}.md", f"{above}{name}.md"):
        if candidate in is_node:
            return candidate
    return
