"""Ask the Phase 6 graph the questions Phase 5 asked SQLite.

The answers must match. Where they diverge, Phase 6 modelled something
wrong - that is what these queries are really testing.
"""

from rdflib.namespace import SKOS

from vault.rdf import V, _class_name, doc_iri, doc_path, tag_iri


def _paths(rows):
    """SPARQL answers in IRIs; SQLite answers in paths. Meet at the path."""
    return sorted(doc_path(row[0]) for row in rows)


def by_type(graph, type_):
    """Every note declaring `type_`, as sorted paths. Mirrors graph.by_type."""
    rows = graph.query(
        "SELECT ?doc WHERE { ?doc a ?class }",
        initNs={"v": V},
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
        initNs={"v": V, "skos": SKOS},
        initBindings={"tag": tag_iri(tag)},
    )
    return _paths(rows)
