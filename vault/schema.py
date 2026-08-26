"""The schema of record, expressed as code. A violation is a refusal."""

import re
from datetime import date

from vault.frontmatter import fm_get, fm_list
from vault.links import strip_code

# Copied from the vault's `Vault 온톨로지 — 스키마 정본`. That document is
# the original; changing anything here means changing it there first.
TYPES = {
    "concept",
    "procedure",
    "principle",
    "decision",
    "tradeoff",
    "case",
    "source-note",
    "review",
    "reflection",
    "project-doc",
    "reference",
    "log",
    "hub",
}

# `template` was removed 2026-08-26. A blank form now carries the type of the
# document it produces, so a note made from an Obsidian template starts out
# correctly typed instead of needing a hand edit. That the file is a form is
# said by its name and its folder, and the schema's own rule is that a fact
# derivable from the path does not go in the frontmatter.

# The four the schema marks 판단 — a person decides them, and a reader picks
# among them without opening the file. Measured 2026-08-18: these carry a
# summary 99~100% of the time (case 60%), every other type under 10%.
# Demanding one everywhere would raise some 2,700 false violations.
NEEDS_SUMMARY = {"concept", "procedure", "reference", "case"}

SUMMARY_MAX = 80
BUILDS_ON_MAX = 3


def validate(fm):
    """Return every rule `fm` breaks, as (code, detail) pairs.

    A list rather than an exception: one document can break several rules
    and the report has to carry all of them. Empty means clean.
    """
    broken = []

    type_ = fm_get(fm, "type")
    if not type_:
        broken.append(("type missing", ""))
    elif type_ not in TYPES:
        broken.append(("type unknown", type_))

    summary = fm_get(fm, "summary")
    if not summary:
        if type_ in NEEDS_SUMMARY:
            broken.append(("summary missing", ""))
    elif len(summary) > SUMMARY_MAX:
        broken.append(("summary too long", f"{len(summary)}자"))

    builds_on = fm_list(fm, "builds_on")
    if len(builds_on) > BUILDS_ON_MAX:
        broken.append(("builds_on too many", f"{len(builds_on)}개"))

    created = fm_get(fm, "created")
    if not created:
        broken.append(("created missing", ""))
    else:
        # The shape is not the value: `2026-13-99` passes any regex you write.
        try:
            date.fromisoformat(created)
        except ValueError:
            broken.append(("created invalid", created))

    return broken


# Obsidian makes `#word` a tag only when the `#` opens a word: the character
# before it must be whitespace, or nothing at all. That one condition drops
# every false positive the old detector patched one at a time —
#     ](#anchor)      markdown link target      before is `(`
#     …com/a#_oidc    URL fragment              before is a letter
#     \#5450          escaped hash              before is `\`
#     [[Docker#설치]]  wikilink heading anchor    before is a letter
#     C#/FNA          hash inside a word        before is a letter
#     # 제목           heading                    a space follows, not a word
BODY_TAG = re.compile(r"(?<![^\s])#([\w/-]+)")


def find_body_tags(body):
    """Return every tag Obsidian would build out of `body`.

    Since the 2026-08-16 migration a tag may only live in the frontmatter
    `tags:` block, so anything found here is a violation — no difference
    between one a person typed and a hex colour that became one by accident.
    """
    return [
        match.group(1)
        for match in BODY_TAG.finditer(strip_code(body))
        if any(char.isalpha() for char in match.group(1))
    ]
