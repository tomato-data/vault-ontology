"""Operating rules over the asserted graph. Nothing here is materialised.

Phase 9 measured what materialising costs: OWL RL tripled the graph and
produced no useful new fact. Phase 17 measured why it would not help here
either — the semantic graph is 159 edges over 275 nodes, and only 5 of
those nodes have an edge in AND an edge out. There is almost nothing to
chain, so a closure would store what a walk finds in milliseconds.

Every rule returns the PATH, not the endpoint. That is why these are walks
in Python rather than SPARQL property paths: `?a v:derived_from+ ?b` gives
the pair and throws away how it got there, and Step 3 asks for exactly the
part it throws away.

Input is the asserted graph only. `proposed:` never enters it (Phase 15
Step 3), so that holds without a check here.
"""

from collections import Counter

from vault.rdf import V

# Rule identity. A result carries the id and version of what produced it,
# so a stored answer can be told apart from a rerun of a changed rule.
VERSION = "17.0"

# The seven of Phase 14. `builds_on` is deliberately absent: it says one
# WRITING stands on another, and mixing it in would let a reading order
# masquerade as a chain of grounds.
SEMANTIC = (
    V.derived_from,
    V.contradicts,
    V.diverges_from,
    V.applies,
    V.informed_by,
    V.expresses,
    V.answered_by,
)

# Depth 2 is the deepest chain in the vault (measured 2026-08-31: 7 of
# them, six being `Decision -> Trade-offs -> 출처`). The cap is not a
# performance guard, it is a statement that a longer path in this data is
# almost certainly a cycle through an alias.
MAX_DEPTH = 6


def _step(graph, node):
    """Every semantic edge leaving `node`, as (predicate, object)."""
    for predicate in SEMANTIC:
        for target in graph.objects(node, predicate):
            yield predicate, target


def genealogy(graph, start, max_depth=MAX_DEPTH):
    """Every chain of grounds leading away from `start`, longest first.

    Answers C02 (the tradeoff and source behind a decision), C04 (the
    event behind a principle) and C09/C15 (a personal value surfacing in a
    technical decision) — one walk, because all three ask the same shape.

    A path is a list of (subject, predicate, object). The caller can print
    it, and every hop names a document that can be opened.

    Cycles are dropped, not raised: `contradicts` is symmetric and a
    two-document disagreement is a legitimate two-cycle, not an error.
    """
    found = []
    stack = [(start, [], frozenset({start}))]
    while stack:
        node, path, seen = stack.pop()
        edges = [
            (predicate, target)
            for predicate, target in _step(graph, node)
            if target not in seen
        ]
        if not edges and path:
            found.append(path)
            continue
        for predicate, target in edges:
            hop = path + [(node, predicate, target)]
            if len(hop) >= max_depth:
                found.append(hop)
            else:
                stack.append((target, hop, seen | {target}))
    found.sort(key=lambda path: (-len(path), [str(x) for hop in path for x in hop]))
    return found


def impact(graph, target):
    """What stands on `target`, one hop back, as (subject, predicate).

    Answers C21 (decisions that applied a principle) and the question
    behind Phase 17's fifth candidate — what breaks if this changes.
    Reverse and shallow on purpose: "what leans on this" is a fact about
    the neighbours, and a transitive version answers a different question.
    """
    leaning = [
        (subject, predicate)
        for predicate in SEMANTIC
        for subject in graph.subjects(predicate, target)
    ]
    leaning.sort(key=lambda pair: (str(pair[1]), str(pair[0])))
    return leaning


def shared_ground(graph, minimum=2):
    """Documents that rest on the same source, grouped by that source.

    Answers C05 and C06 — two principles built on one event may reinforce
    each other or pull apart, and neither shows up until they are put side
    by side. This does not judge which it is; a shape or a person does.
    """
    by_source = {}
    for predicate in SEMANTIC:
        for subject, source in graph.subject_objects(predicate):
            by_source.setdefault(source, set()).add(subject)
    groups = [
        (source, sorted(users, key=str))
        for source, users in by_source.items()
        if len(users) >= minimum
    ]
    groups.sort(key=lambda group: (-len(group[1]), str(group[0])))
    return groups


def invalidated(graph):
    """Documents whose ground is contradicted somewhere.

    Phase 17's headline candidate — "recompute principles resting on an
    invalidated claim". Measured 2026-08-31 it returns NOTHING, because
    the vault holds one `contradicts` and nothing is derived from either
    end of it. Kept, not deleted: the rule is right and the data is thin,
    which is a different situation from a rule that asks a wrong question.
    """
    hit = []
    for subject, source in graph.subject_objects(V.derived_from):
        against = list(graph.objects(source, V.contradicts)) + list(
            graph.subjects(V.contradicts, source)
        )
        hit.extend((subject, source, other) for other in against)
    hit.sort(key=str)
    return hit


def explain(path):
    """Turn a path into lines a person reads, one hop each."""
    from vault.rdf import doc_path, section_path

    def name(node):
        text = str(node)
        if "#" in text:
            document, heading = section_path(node)
            return f"{document}#{heading}"
        return doc_path(node)

    lines = []
    for subject, predicate, obj in path:
        relation = str(predicate).rsplit("/", 1)[-1]
        lines.append(f"{name(subject)}  --{relation}-->  {name(obj)}")
    return lines


def coverage(graph):
    """How many results each rule has to offer. Counts, never answers.

    A rule that returns nothing answers no question, and Phase 14 killed
    eleven classes on exactly that test. This is what keeps the same test
    running as the vault grows.
    """
    subjects = {s for predicate in SEMANTIC for s in graph.subjects(predicate, None)}
    chains = Counter()
    for subject in subjects:
        for path in genealogy(graph, subject):
            chains[len(path)] += 1
    return {
        "genealogy": dict(sorted(chains.items())),
        "shared_ground": len(shared_ground(graph)),
        "invalidated": len(invalidated(graph)),
    }
