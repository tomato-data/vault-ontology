"""The schema of record, expressed as code. A violation is a refusal."""

from datetime import date

from vault.frontmatter import fm_get, fm_list

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
    "reflection",
    "project-doc",
    "reference",
    "log",
    "hub",
    "template",
}

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

    if len(fm_list(fm, "builds_on")) > BUILDS_ON_MAX:
        broken.append(("builds_on too many", f"{len(fm_list(fm, 'builds_on'))}개"))

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
