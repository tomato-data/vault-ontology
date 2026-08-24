"""Turn a vault note into RDF triples.

Identity is decided in `doc_iri` and nowhere else - see docs/iri-policy.md.
"""

from rdflib import Literal, Namespace
from rdflib.namespace import RDF, XSD

from vault.frontmatter import fm_get, fm_list, split_frontmatter
from vault.links import iter_links, link_target

BASE = "https://tomato.vault/"
V = Namespace(BASE + "schema/")
DOC = Namespace(BASE + "doc/")
FOLDER = Namespace(BASE + "folder/")

# An IRI carries most of Unicode, so Korean goes in as it is - that is what
# the `I` buys, and a readable IRI was half the reason paths were chosen at
# all. These few are structurally special and have to be escaped. A single
# `translate` pass, so escaping `%` cannot double-escape what follows.
ESCAPES = str.maketrans(
    {
        " ": "%20",
        "#": "%23",
        "?": "%3F",
        "%": "%25",
        '"': "%22",
        "<": "%3C",
        ">": "%3E",
        "\\": "%5C",
        "^": "%5E",
        "`": "%60",
        "{": "%7B",
        "}": "%7D",
        "|": "%7C",
    }
)


def doc_iri(relative):
    """Mint the IRI for a document. The ONE place identity is decided.

    Path based, per `docs/iri-policy.md`. The `/` stays a separator: encoding
    it would flatten the hierarchy out of the IRI. `.md` comes off, because
    the extension says how the note is stored and not what it is - the same
    document must survive a change of format.

    When the switch to a stable ID comes, this function is the whole cost.
    """
    return DOC[relative.removesuffix(".md").translate(ESCAPES)]


def folder_iri(path):
    """Mint the IRI for a folder.

    Same escaping as a document, a different namespace. Both can carry the
    same path: `200 Dev/Network` is a folder, and dropping `.md` from
    `200 Dev/Network/Network.md` yields a document one segment longer. The
    split guarantees they never collide.
    """
    return FOLDER[path.translate(ESCAPES)]


def _class_name(type_):
    """`source-note` becomes `SourceNote`.

    RDF names classes UpperCamelCase and properties lowerCamelCase, so the
    shape of a name says which of the two it is.
    """
    return "".join(part.capitalize() for part in type_.split("-"))


def node_triples(relative, text):
    """Yield (subject, predicate, object) for one note's own facts.

    A missing field yields NO triple. RDF has no NULL - silence means
    "not stated", never "empty". The open world assumption arrives here,
    at the very first step.
    """
    subject = doc_iri(relative)
    fm, _ = split_frontmatter(text)

    type_ = fm_get(fm, "type")
    if type_:
        # A resource, not a string. Phase 8 has to be able to say
        # `Concept rdfs:subClassOf Document`, and a literal can never be
        # a subject — so a literal here would end the conversation.
        yield subject, RDF.type, V[_class_name(type_)]

    summary = fm_get(fm, "summary")
    if summary:
        yield subject, V.summary, Literal(summary)

    created = fm_get(fm, "created")
    if created:
        # Declaring a type is not checking it: `"2026-13-99"^^xsd:date`
        # serialises happily. Phase 4's lint is what refuses; the model
        # only states. That gap is the subject of Phase 9.
        yield subject, V.created, Literal(created, datatype=XSD.date)


# The frontmatter relations, in the order the schema of record names them.
NAMED = ("builds_on", "supersedes")


def edge_triples(relative, text, resolve):
    """Yield (subject, predicate, object) for one note's relations.

    `resolve(target) -> path | None` is passed in, so this module never
    learns how resolution works — a dict's `.get` is a valid resolver.

    A target that does not land keeps its text on a `_raw` predicate:

        doc:a  v:builds_on      doc:CIDR        resolved, a resource
        doc:a  v:builds_on_raw  "없는 문서"       not resolved, a literal

    RDF has no NULL, so the SQLite `dst IS NULL` row becomes a different
    predicate rather than an empty object. Minting an IRI for the missing
    document would work too — an IRI need not resolve — but then
    `rdfs:range` would let a reasoner declare 357 phantoms to be Documents,
    and two broken links sharing a name would collapse into one resource.

    `v:supersedes_raw` is the NORMAL case, not a fault: that relation
    points at a document the merge deleted.
    """
    subject = doc_iri(relative)
    fm, body = split_frontmatter(text)

    for kind in NAMED:
        for item in fm_list(fm, kind):
            yield from _edge(subject, kind, link_target(item), resolve)

    for target in iter_links(body):
        yield from _edge(subject, "links_to", target, resolve)

    # Derived from the path, and the target is the FOLDER — not the note
    # that happens to represent it. That note is a sibling, not a container.
    directory = relative.rsplit("/", 1)[0] if "/" in relative else ""
    if directory:
        yield subject, V.part_of, folder_iri(directory)


def _edge(subject, kind, target, resolve):
    """One relation, as a resource when it lands and as text when it does not."""
    landed = resolve(target)
    if landed is None:
        yield subject, V[kind + "_raw"], Literal(target)
    elif landed.endswith(".md"):
        yield subject, V[kind], doc_iri(landed)
    # An attachment is neither a relation nor a broken link — Phase 4 cost
    # us 582 false reports before that was clear.


def folder_triples(path, hub=None):
    """Yield what is true of a folder itself.

    A folder is not a file, so SQLite would have needed a fake row and used
    the folder note as a stand-in — which is why `part_of` used to point at
    a sibling and the chain died at depth 2 while paths go 6 deep. An IRI
    costs nothing here, so the compromise is not needed.
    """
    subject = folder_iri(path)
    if "/" in path:
        yield subject, V.part_of, folder_iri(path.rsplit("/", 1)[0])
    if hub:
        # `type: hub` says what a document IS; this says which folder it is
        # FOR. Measured: 76 hubs are no folder's note, and 27 folder notes
        # are not typed hub. Neither stands in for the other.
        yield subject, V.hub, doc_iri(hub)
