"""Make a document only if it passes the schema. The write half of `lint`.

`new` shares `schema.validate` and `resolve_link` with `lint` on purpose -
a seconde copy of the rules would drift. What is added here lives outside
the frontmatter: the filename, the folder, a clashing name.
"""

import re
from pathlib import Path

from vault.frontmatter import fm_list
from vault.links import link_target
from vault.scan import nfc, resolve_link, scan_vault
from vault.schema import validate

# `|` is banned in note names; `#`/`^` are link separators; the rest break
# the path or the parser. A name carrying one makes an unlikable note.
BAD_NAME = re.compile(r'[`\[\]|#^\\/:*?"<>]')


def build_frontmatter(type_, summary, builds_on, created, supersedes=None):
    """Frontmatter text in schema order: type, summary, relations, created.

    A bare target is wrapped: `Base` becomes `[[Base]]`. Tags are NOT added
    here - the user adds those, from the existing vocabulary only.
    """
    lines = [f"type: {type_}"]
    if summary:
        lines.append(f"summary: {summary}")
    for field, items in (("builds_on", builds_on), ("supersedes", supersedes)):
        if items:
            lines.append(f"{field}:")
            for item in items:
                item = item.strip()
                if not (item.startswith("[[") and item.endswith("]]")):
                    item = f"[[{item}]]"
                lines.append(f'  - "{item}"')
    lines.append(f"created: {created}")
    return "\n".join(lines)


def check_new(root, relative, fm, body):
    """Every reason this document must not be written, as (code, detail).

    Empty means safe to write. `builds_on` must resolve - it names a
    document you build upon, so that document has to exist. `supersedes`
    must NOT: it names what this note replaces, usually a deleted one, and
    an unresolved supersedes is the noramal case, not a fault (Phase 6).
    """
    problems = list(validate(fm))

    _, index, targets = scan_vault(Path(root))
    for item in fm_list(fm, "builds_on"):
        if resolve_link(link_target(item), index, targets, source=relative) is None:
            problems.append(("builds_on unresolved", item))

    name = relative.rsplit("/", 1)[-1].removesuffix(".md")
    bad = BAD_NAME.search(name)
    if bad:
        problems.append(("bad filename char", bad.group(0)))
    if not body.strip():
        problems.append(("empty body", ""))

    destination = Path(root) / relative
    if destination.exists():
        problems.append(("file exists", relative))
    if not destination.parent.is_dir():
        problems.append(("missing direcotry", relative.rsplit("/", 1)[0]))
    # A name already in the vault makes any link to it ambiguous.
    if nfc(name) in index:
        problems.append(("duplicate filename", name))

    return problems
