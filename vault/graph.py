"""Pull the vault into three tables. The graph is derived, never the source."""

import sqlite3

from vault.frontmatter import fm_get, fm_list, split_frontmatter
from vault.links import iter_links, link_target
from vault.scan import resolve_link, scan_vault

# `800 TRPG` uses the same `type:` key for game items (완제품 · 원재료 · 마물),
# so mixing it in breaks the axis. `900 Archive` is dead by design. Phase 6
# gets both back through namespaces, which a SQL column cannot offer.
EXCLUDED_ZONES = ("800 TRPG", "900 Archive")
EXCLUDED_FILES = ("CLAUDE.md",)


# DROP before CREATE, because the graph is derived: markdown is the original
# and this is thrown away and rebuilt. No MERGE, no constraint, no migration.
SCHEMA = """
DROP TABLE IF EXISTS node;
DROP TABLE IF EXISTS edge;
DROP TABLE IF EXISTS tag;

CREATE TABLE node (
  path    TEXT PRIMARY KEY,
  name    TEXT NOT NULL,
  zone    TEXT NOT NULL,
  dir     TEXT,
  type    TEXT,
  summary TEXT,
  created TEXT,
  bytes   INTEGER
);
CREATE TABLE edge (
  src  TEXT NOT NULL,
  dst  TEXT,            -- NULL when the link does not land on a node
  raw  TEXT NOT NULL,   -- what was written, kept even when it breaks
  kind TEXT NOT NULL    -- builds_on · supersedes · links_to
);
CREATE TABLE tag (path TEXT NOT NULL, tag TEXT NOT NULL);
"""


def _in_graph(relative):
    """True when this note belongs in the graph at all."""
    if relative in EXCLUDED_FILES:
        return False
    # `zone + "/"`, never a bare prefix: "800 TRPG" must not swallow
    # "800 TRPG Archive". Sixth time this boundary has come up.
    return not any(
        relative == zone or relative.startswith(zone + "/") for zone in EXCLUDED_ZONES
    )


def _folder_note(relative, is_node):
    r"""The note standing in for this note's folder, if there is one.

    Two conventions, both pinned by PATH rather than by name:

        A/B/B.md    the folder note inside the folder
        A/B.md      the folder note beside it

    Never a name lookup. The answer key resolves `B` globally, so a note in
    `200 Dev/Network/` attaches to any `Network.md` anywhere in the vault.
    A name is not an identifier — that was Phase 3's whole subject.
    """
    if "/" not in relative:
        return None  # the vault root has no folder note
    directory = relative.rsplit("/", 1)[0]
    name = directory.rsplit("/", 1)[-1]
    above = directory.rsplit("/", 1)[0] + "/" if "/" in directory else ""
    for candidate in (f"{directory}/{name}.md", f"{above}{name}.md"):
        if candidate != relative and candidate in is_node:
            return candidate
    return None


def build(root, database=":memory:"):
    """Return a connection holding the vault as node/edge/tag."""
    connection = sqlite3.connect(database)
    connection.executescript(SCHEMA)

    notes, index, targets = scan_vault(root)
    inside = [note for note in notes if _in_graph(note)]
    is_node = set(inside)

    nodes, edges, tags = [], [], []
    for relative in inside:
        path = root / relative
        fm, body = split_frontmatter(path.read_text(encoding="utf-8"))
        directory = relative.rsplit("/", 1)[0] if "/" in relative else ""
        nodes.append(
            (
                relative,
                relative.rsplit("/", 1)[-1].removesuffix(".md"),
                relative.split("/")[0],
                directory,
                fm_get(fm, "type"),
                fm_get(fm, "summary"),
                fm_get(fm, "created"),
                path.stat().st_size,
            )
        )

        for kind in ("builds_on", "supersedes"):
            for item in fm_list(fm, kind):
                raw = link_target(item)
                landed = resolve_link(raw, index, targets, source=relative)
                edges.append(
                    (relative, landed if landed in is_node else None, raw, kind)
                )

        for raw in iter_links(body):
            landed = resolve_link(raw, index, targets, source=relative)
            if landed is not None and not landed.endswith(".md"):
                continue  # an attachment is neither a node nor a broken link
            edges.append(
                (relative, landed if landed in is_node else None, raw, "links_to")
            )

        # Derived, never read: the schema of record dropped `part_of` as a
        # field because the path already knows. Storing it would drift the
        # moment a note moves.
        folder_note = _folder_note(relative, is_node)
        if folder_note:
            edges.append(
                (relative, folder_note, directory.rsplit("/", 1)[-1], "part_of")
            )

        tags += [(relative, tag) for tag in fm_list(fm, "tags")]

    connection.executemany("INSERT INTO node VALUES (?,?,?,?,?,?,?,?)", nodes)
    connection.executemany("INSERT INTO edge VALUES (?,?,?,?)", edges)
    connection.executemany("INSERT INTO tag VALUES (?,?)", tags)
    connection.commit()
    return connection
