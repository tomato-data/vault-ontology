"""Pull the vault into three tables. The graph is derived, never the source."""

import sqlite3

from vault.frontmatter import fm_get, fm_list, split_frontmatter
from vault.links import iter_links, link_target
from vault.scan import folder_note, resolve_link, scan_vault

# `900 Archive` is dead by design, so its schema is not ours to judge.
# `800 TRPG` used to sit here too — it reused `type:` for game items and
# broke the axis — but on 2026-08-23 it left the vault for a repository of
# its own. Phase 6 asks whether two corpora that far apart can be merged
# into one graph at all, which is the question RDF namespaces exist for.
EXCLUDED_ZONES = ("900 Archive",)
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


def in_graph(relative):
    """True when this note belongs in the graph at all."""
    if relative in EXCLUDED_FILES:
        return False
    # `zone + "/"`, never a bare prefix: "800 TRPG" must not swallow
    # "800 TRPG Archive". Sixth time this boundary has come up.
    return not any(
        relative == zone or relative.startswith(zone + "/") for zone in EXCLUDED_ZONES
    )


def build(root, database=":memory:"):
    """Return a connection holding the vault as node/edge/tag."""
    connection = sqlite3.connect(database)
    connection.executescript(SCHEMA)

    notes, index, targets = scan_vault(root)
    inside = [note for note in notes if in_graph(note)]
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
        note = folder_note(directory, is_node) if directory else None
        if note and note != relative:
            edges.append(
                (relative, note, directory.rsplit("/", 1)[-1], "part_of")
            )

        tags += [(relative, tag) for tag in fm_list(fm, "tags")]

    connection.executemany("INSERT INTO node VALUES (?,?,?,?,?,?,?,?)", nodes)
    connection.executemany("INSERT INTO edge VALUES (?,?,?,?)", edges)
    connection.executemany("INSERT INTO tag VALUES (?,?)", tags)
    connection.commit()
    return connection


def stats(connection):
    """Return the shape of the graph: table sizes and edges by kind."""
    counts = {
        # The table name arrives by f-string because SQL cannot parameterise
        # an identifier — only a value. Which is exactly why nothing from
        # outside this module may ever reach that position.
        table: connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        for table in ("node", "edge", "tag")
    }
    counts["unresolved"] = connection.execute(
        "SELECT count(*) FROM edge WHERE dst IS NULL"
    ).fetchone()[0]
    counts["kinds"] = dict(
        connection.execute("SELECT kind, count(*) FROM edge GROUP BY kind")
    )
    return counts


def by_type(connection, type_):
    """Return the path of every note of `type_`, sorted."""
    return [
        path
        for (path,) in connection.execute(
            "SELECT path FROM node WHERE type = ? ORDER BY path", (type_,)
        )
    ]


def by_tag(connection, tag):
    """Return every note carrying `tag` or a tag nested under it, sorted.

    `Stack` finds `Stack/Python`, the way clicking a tag does in Obsidian.
    The boundary is the slash: `Stack` must not reach `Stacked`.

    Compared with `substr` rather than `LIKE`, because `_` and `%` are
    wildcards to LIKE and a tag is allowed to contain them.
    """
    nested = tag + "/"
    return [
        path
        for (path,) in connection.execute(
            "SELECT DISTINCT path FROM tag"
            " WHERE tag = ? OR substr(tag, 1, ?) = ?"
            " ORDER BY path",
            (tag, len(nested), nested),
        )
    ]


def learning_path(connection, path, limit=10):
    """Return what to read before `path`, as (path, depth) pairs.

    The transitive closure of `builds_on`, shallowest first, each note
    once at the shortest depth that reaches it.

    `UNION` dedupes whole ROWS, and a row here is (id, depth) — so a cycle
    keeps producing fresh rows with a bigger depth and does NOT stop on its
    own. `depth < :limit` is what ends it. Dropping `depth` from the row
    would let UNION terminate the cycle by itself, at the cost of the one
    number that makes this a reading ORDER rather than a set.
    """
    return list(
        connection.execute(
            "WITH RECURSIVE chain(id, depth) AS ("
            "  SELECT :start, 0"
            "  UNION"
            "  SELECT e.dst, chain.depth + 1"
            "    FROM edge e JOIN chain ON e.src = chain.id"
            "   WHERE e.kind = 'builds_on'"
            "     AND e.dst IS NOT NULL"
            "     AND chain.depth < :limit"
            ")"
            " SELECT id, min(depth) FROM chain"
            "  WHERE id <> :start"
            "  GROUP BY id"
            "  ORDER BY 2, 1",
            {"start": path, "limit": limit},
        )
    )


def near(connection, path):
    """Return the notes around `path`, grouped by how they touch it.

    `shares_tag` leaves out anything already linked either way. Obsidian
    shows links and backlinks already; this third group only earns its
    place by surfacing what following links would never reach — search
    step 4 in the schema of record, 뜻밖의 발견.

    It carries HOW MANY tags are shared, most first, because one shared
    tag is usually not a relation. On the real vault a note tagged
    `Source/Claude` neighbours 45 others that share nothing but their
    author. Which prefixes carry meaning is a judgement with no evidence
    behind it yet, so the count is reported rather than a rule applied.
    """
    out = [
        p
        for (p,) in connection.execute(
            "SELECT DISTINCT dst FROM edge"
            " WHERE src = ? AND dst IS NOT NULL ORDER BY dst",
            (path,),
        )
    ]
    into = [
        p
        for (p,) in connection.execute(
            "SELECT DISTINCT src FROM edge WHERE dst = ? ORDER BY src", (path,)
        )
    ]
    # A note is not its own neighbour, and the tag join would say otherwise.
    known = set(out) | set(into) | {path}
    shared = connection.execute(
        "SELECT other.path, count(*) FROM tag mine"
        "  JOIN tag other ON other.tag = mine.tag"
        " WHERE mine.path = ?"
        " GROUP BY other.path ORDER BY 2 DESC, 1",
        (path,),
    )
    return {
        "links_to": out,
        "linked_by": into,
        "shares_tag": [(p, n) for p, n in shared if p not in known],
    }


def orphans(connection, zone=None):
    """Return every node no edge points at, optionally within one zone."""
    # `dst IS NOT NULL` inside the subquery is not tidiness, it is required:
    # `x NOT IN (…)` evaluates to NULL — never true — the moment the list
    # holds a single NULL, so one broken link would empty this whole result.
    sql = (
        "SELECT path FROM node"
        " WHERE path NOT IN (SELECT dst FROM edge WHERE dst IS NOT NULL)"
    )
    parameters = []
    if zone is not None:
        sql += " AND zone = ?"
        parameters.append(zone)
    return [p for (p,) in connection.execute(sql + " ORDER BY path", parameters)]


DB_NAME = ".vault-graph.db"


def find(connection, needle):
    """Return the path for `needle`, which may be a path or a note name.

    A repeated name resolves to the first in sorted order — the same rule
    as `resolve_link`, with one extra reason here: someone who typed a
    bare name at a prompt has already accepted the ambiguity.
    """
    row = connection.execute(
        "SELECT path FROM node WHERE path = ? OR name = ? ORDER BY path LIMIT 1",
        (needle, needle),
    ).fetchone()
    return row[0] if row else None
