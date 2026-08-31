"""Find the addressable items inside a document.

Phase 13 split the document from the knowledge it holds, and measured where
that split is real: 46 documents write their content as numbered items, and
`_Insights.md` is one v:ReflectionDocument carrying 24 separate beliefs. This
module is the parser for that layer — nothing here mints an IRI or a triple.

Only item headings become sections. Phase 15 measured the alternative: of the
59 `[[doc#heading]]` links in the vault, 58 point at an ordinary heading and
are navigation, not meaning. Those stay flattened to the document, exactly as
before, so `links_to` does not move.
"""

import re

from vault.links import LINK, link_parts, strip_code

# What the vault actually writes. This is a census, not a fixed vocabulary —
# a new prefix belongs on this list the day it appears three times.
ITEM_PREFIXES = ("인사이트", "패턴", "원칙", "교훈", "사례", "규칙", "항목")

# The `#` count is captured: a heading ends the item above it only when it is
# no deeper, so `#### 근거` under `### 인사이트 3` stays inside the insight.
HEADING = re.compile(r"^(#{1,6})[ \t]+(\S.*?)[ \t]*$")

# A prefix and a number, and the number must end. `\d+` alone would let
# `인사이트 1` name `인사이트 10`, which is the same off-by-nine that makes
# `resolve_anchor` below an exact match rather than a prefix one.
ITEM = re.compile(r"^(" + "|".join(ITEM_PREFIXES) + r")[ \t]*(\d+)(?![\d])")

# `인사이트 3: TDD 자동화 = 학습 효율` — the link carries only what is left of
# this. A fullwidth colon reads the same to a person, so it counts too.
COLON = re.compile(r"[:：]")

# Three of one prefix. Below that, a document numbering two paragraphs is
# just a document; above it, the author is addressing items one by one.
CARRIER_THRESHOLD = 3

# `인사이트 20: … (2026-03-22)` — when the item says it holds, which is not
# when the file was written. The bracket is required: measured 2026-08-31,
# all 74 dated items use it and none writes the date bare, so demanding it
# keeps a date that belongs to the TITLE out of `as_of`.
AS_OF = re.compile(r"\((\d{4}-\d{2}-\d{2})")


def _headings(body):
    """Yield (level, text) for every heading, code blanked out first."""
    for line in strip_code(body).split("\n"):
        match = HEADING.match(line)
        if match:
            yield len(match.group(1)), match.group(2)


def item_headings(body):
    """The document's addressable items, in order, exactly as written.

    Empty unless the document carries at least three numbered items of one
    prefix. The threshold decides the DOCUMENT, not the heading: once a
    document is addressed item by item, its lone `패턴 1` is addressable too.
    """
    items = [text for _, text in _headings(body) if ITEM.match(text)]
    counts = {}
    for text in items:
        prefix = ITEM.match(text).group(1)
        counts[prefix] = counts.get(prefix, 0) + 1
    if not counts or max(counts.values()) < CARRIER_THRESHOLD:
        return []
    return items


def resolve_anchor(headings, anchor):
    """Return the heading an anchor names, or None.

    Exact match, against the whole heading or against what stands before its
    first colon. NOT a prefix match — `인사이트 1` would then also answer for
    `인사이트 10` and the fact would land on the wrong belief.
    """
    for heading in headings:
        if anchor in (heading, COLON.split(heading, 1)[0].strip()):
            return heading
    return None


def item_date(heading):
    """The date an item states for itself, or None.

    This is `v:as_of` and not `dcterms:created`: it says when the belief
    held, while the file's `created` says when it was typed up. C08 — how a
    belief changed and when — needs the first and gets nothing from the
    second, because 24 insights share one file date.

    The first date wins. A range (`2026-04-29 ~ 04-30`) is dated by where
    it started, which is what a range's `as_of` means.

    Only the heading is read. The `**Last Updated**` line at the foot of a
    document looks like an item's update date and is not one: of 11 lines
    matching that shape, 10 sat under the LAST item and 8 were the file's
    own footer. Three genuine `> **날짜 갱신 (…)**:` blocks survive, which
    is too few to write a rule for.
    """
    match = AS_OF.search(heading)
    return match.group(1) if match else None


def iter_links_by_item(body):
    """Yield (item, document, heading) for every wikilink in `body`.

    `item` is the item heading the link sits under, or None when it sits in
    the document at large. That is the whole point of the layer: the gold set
    measured 500 as unlabelable at document level because its links hang off
    individual insights, and this is what moves those links onto them.
    """
    items = set(item_headings(body))
    current = None
    for line in strip_code(body).split("\n"):
        match = HEADING.match(line)
        if match:
            level, text = len(match.group(1)), match.group(2)
            if text in items:
                current = (level, text)
            elif current and level <= current[0]:
                current = None
            continue
        for found in LINK.finditer(line):
            document, heading = link_parts(found.group(1))
            if document:
                yield (current[1] if current else None), document, heading
