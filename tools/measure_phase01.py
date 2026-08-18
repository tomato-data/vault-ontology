"""Run the Phase 1 parser over the whole vault and count what it sees.

Throwaway measurement, not library code. No tests, no reuse.
    uv run python -m tools.measure_phase01
"""

import re
from collections import Counter
from pathlib import Path

from vault.frontmatter import fm_get, fm_list, split_frontmatter

VAULT = Path.home() / (
    "Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault"
)

# The answer key builds its graph from everything BUT these. `800 TRPG` reuses
# the same `type:` key for game items, so mixing it in breaks the axis.
EXCLUDED = ("800 TRPG", "900 Archive", ".claude", ".trash", ".obsidian")

# Schema of record — 13 values.
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
SUMMARY_MAX = 80

# A key line, a blank line, then a bullet. `fm_list` drops this block silently.
BLANK_IN_BLOCK = re.compile(r"^[a-z_]+:[ \t]*\n\n[ \t]+- ", re.M)


def measure(paths):
    """Count what the parser reads across `paths`."""
    count = Counter()
    types = Counter()
    lengths = []
    for path in paths:
        count["files"] += 1
        fm, _ = split_frontmatter(path.read_text(encoding="utf-8"))
        if fm is None:
            continue
        count["frontmatter"] += 1
        if BLANK_IN_BLOCK.search(fm):
            count["blank line in a block"] += 1

        type_ = fm_get(fm, "type")
        if type_:
            count["type"] += 1
            types[type_] += 1

        summary = fm_get(fm, "summary")
        if summary:
            count["summary"] += 1
            lengths.append(len(summary))

        for key in ("builds_on", "supersedes"):
            items = fm_list(fm, key)
            if items:
                count[f"{key} docs"] += 1
                count[f"{key} items"] += len(items)
    return count, types, lengths


def report(title, paths):
    count, types, lengths = measure(paths)
    files = count["files"]
    print(f"\n=== {title} ===")
    for key in (
        "files",
        "frontmatter",
        "type",
        "summary",
        "builds_on docs",
        "builds_on items",
        "supersedes docs",
        "supersedes items",
        "blank line in a block",
    ):
        print(f"{key:24} {count[key]:6,} {count[key] / files:6.1%}")

    if lengths:
        lengths.sort()
        print(f"\nsummary length")
        print(f"  min      {lengths[0]:6,}")
        print(f"  median   {lengths[len(lengths) // 2]:6,}")
        print(f"  p95      {lengths[int(len(lengths) * 0.95)]:6,}")
        print(f"  max      {lengths[-1]:6,}")
        print(f"  over {SUMMARY_MAX}  {sum(n > SUMMARY_MAX for n in lengths):6,}")
    print("\ntype")
    for name, n in types.most_common():
        flag = "" if name in TYPES else "   <-- outside the schema"
        print(f"  {name:16} {n:6,}{flag}")


def main():
    paths = sorted(VAULT.rglob("*.md"))
    included = [p for p in paths if not str(p.relative_to(VAULT)).startswith(EXCLUDED)]
    report("whole vault", paths)
    report("graph zones only", included)


if __name__ == "__main__":
    main()
