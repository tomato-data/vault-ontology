"""Run the Phase 2 link parser over the whole vault and count what it sees.

Throwaway measurement, not library code.
    uv run python -m tools.measure_phase02
"""

import re
from collections import Counter
from pathlib import Path

from vault.frontmatter import fm_list, split_frontmatter
from vault.links import iter_links, link_target, strip_code

VAULT = Path.home() / (
    "Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault"
)
EXCLUDED = ("800 TRPG", "900 Archive", ".claude", ".trash", ".obsidian")

# Things the parser knowingly does not handle. Count them before deciding.
TILDE_FENCE = re.compile(r"^[ \t]*~~~", re.M)
LONG_FENCE = re.compile(r"^[ \t]*(`{4,}|~{4,})", re.M)
DOUBLE_TICK = re.compile(r"(?<!`)``(?!`)")
SEPARATORS = ("|", "#", "^")


def measure(paths):
    count = Counter()
    for path in paths:
        count["files"] += 1
        text = path.read_text(encoding="utf-8")
        name = path.stem
        if any(sep in name for sep in SEPARATORS):
            count["file name holds a separator"] += 1

        fm, body = split_frontmatter(text)

        # Frontmatter edges — do they need link_target too?
        for key in ("builds_on", "supersedes"):
            for item in fm_list(fm, key):
                count["frontmatter edges"] += 1
                if link_target(item) != item:
                    count["frontmatter edge holds a separator"] += 1

        # Body links.
        links = list(iter_links(body))
        count["links"] += len(links)
        if links:
            count["files with a link"] += 1

        # Knwon gaps in strip_code.
        if TILDE_FENCE.search(text):
            count["tilde fence"] += 1
        if LONG_FENCE.search(text):
            count["fence of four or more"] += 1
        if DOUBLE_TICK.search(text):
            count["double backtick"] += 1

        # How much does stripping code actually remove?
        if len(list(iter_links(text))) != len(links):
            count["frontmatter would double count"] += 1
    return count


def report(title, paths):
    count = measure(paths)
    print(f"\n=== {title} ===")
    for key in (
        "files",
        "links",
        "files with a link",
        "frontmatter edges",
        "frontmatter edge holds a separator",
        "file name holds a separator",
        "tilde fence",
        "fence of four or more",
        "double backtick",
        "frontmatter would double count",
    ):
        print(f"{key:36} {count[key]:7,}")


def main():
    paths = sorted(VAULT.rglob("*.md"))
    included = [p for p in paths if not str(p.relative_to(VAULT)).startswith(EXCLUDED)]
    report("whole vault", paths)
    report("graph zones only", included)


if __name__ == "__main__":
    main()
