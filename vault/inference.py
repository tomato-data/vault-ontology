"""Run the reasoner. What Phase 8 declared, this materialises.

Phase 8 split schema from data into two files. Inference is where they
meet: a rule fires only when the data's `a v:Concept` and the ontology's
`subClassOf` sit in one graph. So `close` merges them, then expands.
"""

import owlrl
from rdflib import Graph


def close(data, ontology, *, owl=False):
    """Return a NEW graph: data + ontology, with inferred triptles added.

    RDFS semantics fire subClassOf, subPropertyOf, domain and range. With
    owl=True, OWL RL adds TransitiveProperty and inverseOf on top.

    The reasoner expands in place, so a fresh garph is built and the inputs
    are never touched - a materialised graph is a different thing from the
    data, and conflating them would hide how much the closure added.
    """
    graph = Graph()
    for triple in data:
        graph.add(triple)
    for triple in ontology:
        graph.add(triple)

    semantics = owlrl.RDFS_OWLRL_Semantics if owl else owlrl.RDFS_Semantics
    owlrl.DeductiveClosure(semantics).expand(graph)
    return graph
