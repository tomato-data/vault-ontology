"""The tag vocabulary — what may be tagged from, and when it may grow.

`vault tags` is read-only on purpose. Adding a tag is a separate, deliberate
act, so an agent handed this list cannot grow the vocabulary — which is the
failure mode that made auto-tagging unpleasant before. Thirty-odd hex colour
tags got in that way and had to be swept out.

The schema of record says the rule precisely:

    「태그 체계는 유지·검수만 한다. 새 축을 태그로 만들지 않는다」

**축, not 값.** A new AXIS is a new dimension of classification and stays
banned. A new VALUE inside an existing axis is how a vocabulary follows a
vault that keeps growing, and freezing that was never what the rule said.

Measured 2026-09-01, the vocabulary is not overgrown — it is unused:

    문서 4,043 · 어휘 244 · 부착 3,157
    태그 없는 문서 2,078 (51%)   ·   문서당 중앙값 0

So the gate below is not a brake. It is a way to tell the two failure modes
apart: a value that names something real, and a value that is somebody's
passing judgement.
"""

from collections import Counter
from math import log2

from vault.frontmatter import fm_list, split_frontmatter
from vault.graph import in_graph
from vault.scan import scan_vault

# An axis whose values name something that exists outside the vault — a
# person, a project, a tool, a technology. A new value here invents no
# category; it records that the thing turned up. Adding is free, and a
# value used once is normal (`Person/정준영` is one person).
#
# Everything else is judgemental: the value is a call somebody made, and
# `Genre/입문서` could as easily have been three other words. Those need a
# reason, and singletons piling up there is the hex-colour shape returning.
REFERENTIAL = ("Person", "Projects", "Source", "Stack")

# A value covering this much of its axis has stopped telling anything apart
# inside it. `review` was born exactly here: `source-note` held 1,252 of
# 1,258 documents in 600 until it was split.
DOMINANT = 0.5

# Singletons above this share of a judgemental axis say the axis is being
# used as a scratchpad rather than a vocabulary.
SCRATCH = 0.4

# What the gate can answer.
KNOWN = "known"  # already in the vocabulary
FREE = "free"  # a referential axis — name it and move on
NEEDS_REASON = "needs-reason"  # a judgemental axis — say what it splits
NEW_AXIS = "new-axis"  # refused. this is the rule that stands


def tag_vocabulary(root):
    """Every tag in the graph zones with its note count, commonest first."""
    counts = Counter()
    notes, _, _ = scan_vault(root)
    for relative in notes:
        if not in_graph(relative):
            continue
        fm, _ = split_frontmatter((root / relative).read_text(encoding="utf-8"))
        counts.update(fm_list(fm, "tags"))
    return counts.most_common()


def axis(tag):
    """The axis a tag belongs to — everything before the first slash."""
    return tag.split("/", 1)[0]


def judge(vocabulary, proposed):
    """Return (verdict, reason) for a tag someone wants to add.

    The vocabulary is a mapping of tag to use count — what `tag_vocabulary`
    returns, as a dict. Nothing here writes; the answer is for a person or
    for the report below.
    """
    if proposed in vocabulary:
        return KNOWN, f"이미 있다 ({vocabulary[proposed]}개 문서)"

    name = axis(proposed)
    known = {axis(tag) for tag in vocabulary}
    if name not in known:
        return NEW_AXIS, f"「{name}」은 새 축이다 — 정본이 금지한다"

    if name in REFERENTIAL:
        return FREE, f"{name} 은 지시형 축이다 — 실재하는 것을 이름 짓는 것뿐"

    return NEEDS_REASON, f"{name} 은 판단형 축이다 — 무엇을 가르는지 적어야 한다"


def health(vocabulary, untagged=0, documents=0):
    """Per-axis diagnosis, worst first.

    Three signals, and none of them is "the vocabulary is too big":

        split     한 값이 축의 절반을 먹었다.  그 자리가 안 갈린다
        scratch   판단형 축에 1회용이 쌓였다.  어휘가 아니라 낙서다
        unused    태그 자체가 안 붙는다.  가장 큰 숫자가 여기 있다
    """
    by_axis = {}
    for tag, count in vocabulary.items():
        by_axis.setdefault(axis(tag), Counter())[tag] = count

    report = []
    for name, values in by_axis.items():
        total = sum(values.values())
        top, top_count = values.most_common(1)[0]
        singles = [tag for tag, count in values.items() if count == 1]
        kind = "지시형" if name in REFERENTIAL else "판단형"

        # Both signals are about JUDGEMENTAL axes only. A referential axis
        # where one value dominates just says you write about that thing a
        # lot — `Person/안동혁` at 60% is not a vocabulary fault and
        # splitting it would name a person twice.
        signals = []
        if kind == "판단형":
            if top_count / total >= DOMINANT:
                signals.append(
                    ("split", f"{top} 이 {top_count}/{total} ({top_count / total:.0%})")
                )
            if values and len(singles) / len(values) >= SCRATCH:
                signals.append(("scratch", f"1회용 {len(singles)}/{len(values)}"))

        report.append(
            {
                "axis": name,
                "kind": kind,
                "values": len(values),
                "uses": total,
                "share": top_count / total,
                "singles": len(singles),
                "spread": _spread(values),
                "signals": signals,
            }
        )
    report.sort(key=lambda row: (-len(row["signals"]), -row["uses"]))
    if documents:
        report.append(
            {
                "axis": "",
                "kind": "",
                "values": 0,
                "uses": 0,
                "share": 0.0,
                "singles": 0,
                "spread": 0.0,
                "signals": [
                    (
                        "unused",
                        f"태그 없는 문서 {untagged:,}/{documents:,} ({untagged / documents:.0%})",
                    )
                ]
                if untagged
                else [],
            }
        )
    return report


def _spread(values):
    """How evenly an axis uses its values, 0 to 1.

    Normalised entropy. Near 1 the axis is working — every value carries
    its share. Near 0 one value has swallowed the axis, which is the
    `split` signal seen from the other side.
    """
    total = sum(values.values())
    if len(values) < 2 or not total:
        return 0.0
    bits = -sum((n / total) * log2(n / total) for n in values.values())
    return bits / log2(len(values))


def tag_health(root):
    """Read the vault and diagnose. The CLI's entry point."""
    counts = Counter()
    untagged = documents = 0
    notes, _, _ = scan_vault(root)
    for relative in notes:
        if not in_graph(relative):
            continue
        documents += 1
        fm, _ = split_frontmatter((root / relative).read_text(encoding="utf-8"))
        tags = fm_list(fm, "tags")
        if not tags:
            untagged += 1
        counts.update(tags)
    return health(counts, untagged, documents)
