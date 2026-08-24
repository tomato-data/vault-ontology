"""Turn a vault note into RDF triples.

Identity is decided in `doc_iri` and nowhere else - see docs/iri-policy.md.
"""

from rdflib import Literal, Namespace
from rdflib.namespace import RDF, XSD

from vault.frontmatter import fm_get, split_frontmatter

BASE = "https://tomato.vault/"
V = Namespace(BASE + "schema/")
DOC = Namespace(BASE + "doc/")

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
