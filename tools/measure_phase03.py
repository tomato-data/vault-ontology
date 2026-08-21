"""Resolve every wikilink in the vault and count what does not land.

Throwaway measurement, not library code.
    uv run python -m tools.measure_phase03
"""

import time
import unicodedata
from collections import Counter
from pathlib import Path

from vault.frontmatter import fm_list, split_frontmatter
from vault.links import iter_links, link_target
from vault.scan import case_collisions, duplicate_names, resolve_link, scan_vault

VAULT = Path.home() / (
    "Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault"
)
EXCLUDED = ("800 TRPG", "900 Archive", ".claude", ".trash", ".obsidian")

# The answer key's `.vault-lint.json` treats these as expected, not broken.
PLACEHOLDERS = {"...", "참조", "파일명", "제목", "경로", "예시"}


def main():
    started = time.perf_counter()
    notes, index, targets = scan_vault(VAULT)
    print(f"scan_vault          {len(notes):7,} files   "
          f"{time.perf_counter() - started:.2f}s")

    # Resolution always sees the whole vault, the way Obsidian does. Only the
    # counting is split, so the graph-zone column is comparable to the answer key.
    count = Counter()
    unresolved = Counter()
    started = time.perf_counter()
    for relative in notes:
        zone = "all" if relative.startswith(EXCLUDED) else "zone"
        fm, body = split_frontmatter((VAULT / relative).read_text(encoding="utf-8"))

        for target in iter_links(body):
            count["links/all"] += 1
            if zone == "zone":
                count["links/zone"] += 1
            if resolve_link(target, index, targets, source=relative) is None:
                count["unresolved/all"] += 1
                if zone == "zone":
                    count["unresolved/zone"] += 1
                unresolved[target] += 1

        for key in ("builds_on", "supersedes"):
            for item in fm_list(fm, key):
                count["edges/all"] += 1
                if zone == "zone":
                    count["edges/zone"] += 1
                if resolve_link(link_target(item), index, targets,
                                source=relative) is None:
                    count["edges unresolved/all"] += 1
                    if zone == "zone":
                        count["edges unresolved/zone"] += 1
                    unresolved[link_target(item)] += 1
    elapsed = time.perf_counter() - started

    print(f"\n{'':22}{'전체':>9}{'제외 후':>10}")
    for label, key in (("본문 링크", "links"), ("  미해결", "unresolved"),
                       ("frontmatter 엣지", "edges"),
                       ("  미해결", "edges unresolved")):
        print(f"{label:22}{count[key + '/all']:9,}{count[key + '/zone']:10,}")
    rate = count["unresolved/all"] / max(count["links/all"], 1)
    print(f"{'미해결 비율':22}{rate:9.1%}")
    print(f"{'해석 시간':22}{elapsed:8.1f}s")

    placeholders = sum(n for t, n in unresolved.items() if t in PLACEHOLDERS)
    print(f"\n미해결 타깃 {len(unresolved):,}종 · 자리표시자 {placeholders:,}회")
    print("\n가장 많이 깨진 타깃 20")
    for target, n in unresolved.most_common(20):
        print(f"  {n:5,}  {target}")

    print("\n=== 이름이 식별자가 아니라는 증거 ===")
    duplicates = duplicate_names(index)
    collisions = case_collisions(index)
    # Compare against what the filesystem actually handed us, not against the
    # normalised list — otherwise this counts "has Korean in it", not "changed".
    decomposed = sum(1 for p in VAULT.rglob("*.md")
                     if not any(part.startswith(".") for part in p.relative_to(VAULT).parts)
                     and p.name != unicodedata.normalize("NFC", p.name))
    print(f"동명이인            {len(duplicates):5,} 이름 "
          f"({sum(len(v) for v in duplicates.values()):,} 파일)")
    print(f"대소문자 충돌       {len(collisions):5,} 무리")
    print(f"NFD 로 저장된 이름  {decomposed:5,} 파일")

    print("\n동명이인 상위 10")
    for name, where in sorted(duplicates.items(), key=lambda kv: -len(kv[1]))[:10]:
        print(f"  {len(where):3}개  {name}")

    if collisions:
        print("\n대소문자 충돌")
        for names in collisions.values():
            print(f"  {names}")


if __name__ == "__main__":
    main()
