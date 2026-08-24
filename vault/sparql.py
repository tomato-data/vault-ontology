"""Ask the Phase 6 graph the questions Phase 5 asked SQLite.

The answers must match. Where they diverge, Phase 6 modelled something
wrong - that is what these queries are really testing.
"""

from rdflib.namespace import SKOS

from vault.rdf import V, _class_name, doc_iri, doc_path, tag_iri

# Declared once. An unused prefix costs nothing - it is only a binding.
_NS = {"v": V, "skos": SKOS}


def _paths(rows):
    """SPARQL answers in IRIs; SQLite answers in paths. Meet at the path."""
    return sorted(doc_path(row[0]) for row in rows)


def by_type(graph, type_):
    """Every note declaring `type_`, as sorted paths. Mirrors graph.by_type."""
    rows = graph.query(
        "SELECT ?doc WHERE { ?doc a ?class }",
        initNs=_NS,
        initBindings={"class": V[_class_name(type_)]},
    )
    return _paths(rows)


def by_tag(graph, tag):
    """Every note under `tag`, nesting included, as sorted paths.

    `Stack` reaches `Stack/Python` the way clicking a tag does in Obsidian.
    Phase 5 walked the prefix with `substr`; here the hierarchy is real
    triples. A document's own tag climbs `skos:broader*` - zero or more
    steps up - and a note is in if an ancestor it reaches is `?tag`.
    """
    rows = graph.query(
        "SELECT ?doc WHERE { ?doc v:tagged/skos:broader* ?tag }",
        initNs=_NS,
        initBindings={"tag": tag_iri(tag)},
    )
    return _paths(rows)


def summaries(graph, type_):
    """Every note of `type_` with its summary, notes lacking one included.

    Bare pattern matching is an inner join - a note with no summary triple
    would vanish. `OPTIONAL` keeps it and leaves the summary unbound, which
    rdflib hands back as None, right where SQLite would put NULL.
    """
    rows = graph.query(
        "SELECT ?doc ?summary WHERE {"
        " ?doc a ?class ."
        " OPTIONAL { ?doc v:summary ?summary }"
        " }",
        initNs=_NS,
        initBindings={"class": V[_class_name(type_)]},
    )
    return sorted(
        (doc_path(doc), str(summary) if summary is not None else None)
        for doc, summary in rows
    )


def prerequisites(graph, path):
    """Every note reachable from `path` through builds_on, as sorted paths.

    `builds_on+` is the transitive closure the recursive CTE spelled out.
    It answers reachability - a SET - and drops the depth, so this is
    `prerequisites`, not a `learning_path`: no reading order survives.
    A cycle terminates on its own here, where the CTE needed depth < limit.
    """
    rows = graph.query(
        "SELECT ?prereq WHERE {"
        " ?start v:builds_on+ ?prereq ."
        " FILTER(?prereq != ?start)"
        " }",
        initNs=_NS,
        initBindings={"start": doc_iri(path)},
    )
    return sorted(doc_path(row[0]) for row in rows)


def neighbours(graph, path):
    """Every note linked to `path` in either direction, as sorted paths.

    `v:links_to` is the forward link, `^v:links_to` the backlink, and `|`
    unions them. Phase 5 ran two queries and merged the sets in Python;
    the reverse arrow does it in one pattern. A note linked both ways
    matches twice, so DISTINCT dedupes the bag the way UNION did. A note
    is not its own neighbour, so the self-link a cycle makes is filtered.
    """
    rows = graph.query(
        "SELECT DISTINCT ?neighbour WHERE {"
        " ?path (v:links_to|^v:links_to) ?neighbour ."
        " FILTER(?neighbour != ?path)"
        " }",
        initNs=_NS,
        initBindings={"path": doc_iri(path)},
    )
    return sorted(doc_path(row[0]) for row in rows)
