"""Answer a competency question, with the path that produced the answer.

Phase 10 wrote thirty questions; Phase 18 makes the answerable ones run.
The contract here is the ANSWER, not the query: nothing that leaves this
module is an rdflib term, so the engine underneath can change without the
caller noticing. That is Step 4, paid for up front rather than promised.

An empty result is not "there is none". The open world assumption arrives
at exactly this line, and `status` is where it is spelled out.
"""

from typing import NamedTuple

from vault.rdf import EXTERNAL as EXTERNAL_NS
from vault.rdf import V, doc_path, section_path
from vault.rules import SEMANTIC, genealogy, impact, invalidated, shared_ground

# Why an empty answer is empty, in a person's terms. Six, not one, because
# a query returning zero rows says only the last of them.
#
# The split between LIVED, EXTERNAL and BROKEN arrived on 2026-09-01. Until
# then all three landed on `_raw` and `ask` reported a broken link as
# "the source is lived" — a false statement the graph could not correct,
# because the parser had already thrown the difference away.
ANSWERED = "answered"  # a document, in the vault
LIVED = "lived"  # v:experience — it came out of work I did
EXTERNAL = "external"  # ext: — outside the vault
SEARCHED = "searched"  # source_unknown — looked for and absent
BROKEN = "broken"  # `_raw` — a name that lands nowhere. an error
UNRECORDED = "unrecorded"  # nothing is written — NOT "there is none"

# The bands, split the way the questions split. C09 asks whether a personal
# criterion surfaced in a technical decision, and that only means something
# if the two sides are named.
PERSONAL = ("100 Private Log", "500 Mind Compiler", "700 Life Stack")
TECHNICAL = ("200 Dev Knowledge Base", "300 Runtime", "400 Logic Forge")

STATUS_NOTE = {
    ANSWERED: "적혀 있다",
    LIVED: "출처가 문서가 아니라 겪은 일이다",
    EXTERNAL: "출처가 vault 밖에 있다",
    SEARCHED: "찾아봤고 없었다",
    BROKEN: "적힌 이름이 아무 데도 안 닿는다 — 고쳐야 한다",
    UNRECORDED: "아직 안 적혔다 — 없다는 뜻이 아니다",
}


class Hop(NamedTuple):
    """One relation, both ends named the way a person opens them."""

    source: str
    source_heading: str
    relation: str
    target: str
    target_heading: str

    def __str__(self):
        def where(path, heading):
            return f"{path}#{heading}" if heading else path

        return (
            f"{where(self.source, self.source_heading)}"
            f"  --{self.relation}-->  "
            f"{where(self.target, self.target_heading)}"
        )


class Answer(NamedTuple):
    """What a question returned, and why.

    `paths` is a list of chains; each chain is the derivation. An answer
    with no path is not a failure — read `status` before reading `paths`.
    """

    question: str
    subject: str
    status: str
    paths: list
    note: str
    shape: str = "chain"

    def __bool__(self):
        return bool(self.paths)


def _name(node):
    """Split a node IRI into (name a person opens, heading).

    A sentinel is not a file. `doc_path` would hand back
    `schema/experience.md`, which names nothing and reads as if it did.
    """
    text = str(node)
    if node == V.experience:
        return "experience", ""
    if text.startswith(str(EXTERNAL_NS)):
        return "ext:" + text[len(str(EXTERNAL_NS)) :], ""
    if "#" in text:
        return section_path(node)
    return doc_path(node), ""


def _hop(triple):
    subject, predicate, obj = triple
    source, source_heading = _name(subject)
    target, target_heading = _name(obj)
    return Hop(
        source,
        source_heading,
        str(predicate).rsplit("/", 1)[-1],
        target,
        target_heading,
    )


def _status(graph, node):
    """Why an answer reads the way it does.

    A document with no relation has said nothing about its grounds; one
    naming `experience` has said something the graph cannot follow to
    another file; one with a broken name has made a mistake. Collapsing
    those turns a recorded fact into a silence, or an error into a fact.
    """
    grounds = [
        target for predicate in SEMANTIC for target in graph.objects(node, predicate)
    ]
    if any(target == V.experience for target in grounds):
        return LIVED
    if any(str(target).startswith(str(EXTERNAL_NS)) for target in grounds):
        return EXTERNAL
    if grounds:
        return ANSWERED
    if any(graph.objects(node, V.source_unknown)):
        return SEARCHED
    for predicate in SEMANTIC:
        if any(graph.objects(node, V[str(predicate).rsplit("/", 1)[-1] + "_raw"])):
            return BROKEN
    return UNRECORDED


def lineage(graph, node):
    """Every chain of grounds behind this document. C02 · C04 · C09 · C15."""
    paths = [[_hop(triple) for triple in path] for path in genealogy(graph, node)]
    status = _status(graph, node)
    return Answer("lineage", _name(node)[0], status, paths, STATUS_NOTE[status])


def evidence(graph, node):
    """Only the first hop. C02's "what is this resting on", nothing further.

    Separate from `lineage` because the questions differ: "what grounds
    this" is answered by the neighbours, and a three-hop chain answers
    "how did this come about" — burying the first answer inside the second
    is how a report stops being read.
    """
    paths = [
        [_hop((node, predicate, target))]
        for predicate in SEMANTIC
        for target in graph.objects(node, predicate)
    ]
    # A `_raw` ground is an answer, not an absence. `derived_from:
    # experience` says the source is lived, and dropping it here would
    # report the document as having said nothing about its grounds.
    raw = [
        Hop(_name(node)[0], _name(node)[1], name + "_raw", str(target), "")
        for name in (str(p).rsplit("/", 1)[-1] for p in SEMANTIC)
        for target in graph.objects(node, V[name + "_raw"])
    ]
    paths.extend([hop] for hop in raw)
    paths.sort(key=lambda path: (path[0].relation, path[0].target))
    status = _status(graph, node)
    return Answer("evidence", _name(node)[0], status, paths, STATUS_NOTE[status])


def affected(graph, node):
    """What leans on this document. C21 · C29 · "what breaks if I change it"."""
    paths = [
        [_hop((subject, predicate, node))] for subject, predicate in impact(graph, node)
    ]
    status = ANSWERED if paths else UNRECORDED
    return Answer("affected", _name(node)[0], status, paths, STATUS_NOTE[status])


def review(graph):
    """Grounds that something else contradicts. C03 · C30.

    Returns nothing today — the vault holds one `contradicts` and nothing
    is derived from either end of it. The empty answer says `unrecorded`,
    which is the honest reading: not "no principle rests on a refuted
    claim", but "no contradiction has been written down where one would
    show".
    """
    paths = [
        [_hop((subject, V.derived_from, source)), _hop((source, V.contradicts, other))]
        for subject, source, other in invalidated(graph)
    ]
    status = ANSWERED if paths else UNRECORDED
    return Answer("review", "", status, paths, STATUS_NOTE[status])


def crossing(graph, left=PERSONAL, right=TECHNICAL):
    """Chains running between a life and the work. C07 · C09 · C15.

    NOT "any two bands". Measured 2026-08-31, 103 of the vault's 163
    chains run 200 to 300 — one technical band to another — so a rule
    that counts any crossing returns 145 of 163 and filters nothing. The
    phase says as much: showing many connections is not the goal.

    Not similarity either. A chain is here because someone wrote the
    relation, which is Phase 17 Step 1's rule — shared words and vector
    scores do not make a `derived_from`.
    """
    subjects = {s for predicate in SEMANTIC for s in graph.subjects(predicate, None)}
    found = []
    for subject in subjects:
        for path in genealogy(graph, subject):
            hops = [_hop(triple) for triple in path]
            touched = {hop.source.split("/", 1)[0] for hop in hops}
            touched |= {hop.target.split("/", 1)[0] for hop in hops}
            if touched & set(left) and touched & set(right):
                found.append(hops)
    found.sort(key=lambda hops: (-len(hops), hops[0].source))
    status = ANSWERED if found else UNRECORDED
    return Answer("crossing", "", status, found, STATUS_NOTE[status])


def together(graph, minimum=2):
    """Documents resting on one source. C05 · C06.

    A group, not a chain: every hop in a group shares its TARGET, and
    rendering it as a chain would read as "A came from B came from B".
    `shape` says which, so the renderer never has to guess.
    """
    paths = [
        [_hop((user, V.derived_from, source)) for user in users]
        for source, users in shared_ground(graph, minimum)
    ]
    status = ANSWERED if paths else UNRECORDED
    return Answer("together", "", status, paths, STATUS_NOTE[status], "group")


def _where(path, heading):
    return f"{path}#{heading}" if heading else path


def render(answer):
    """The answer as lines: the head once, then one arrow per hop.

    Repeating the source on every line doubled the width and made a
    three-hop chain unreadable in a terminal. A chain reads as a chain.
    """
    lines = []
    for path in answer.paths:
        if answer.shape == "group":
            # One source, and everything standing on it.
            lines.append(f"  {_where(path[0].target, path[0].target_heading)}")
            for hop in path:
                lines.append(
                    f"      <--{hop.relation}--  "
                    f"{_where(hop.source, hop.source_heading)}"
                )
        else:
            lines.append(f"  {_where(path[0].source, path[0].source_heading)}")
            for hop in path:
                lines.append(
                    f"      --{hop.relation}-->  "
                    f"{_where(hop.target, hop.target_heading)}"
                )
        lines.append("")
    if not lines:
        lines.append(f"  ({answer.status}) {answer.note}")
    return lines
