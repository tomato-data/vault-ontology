"""Run every question against the real vault and count what comes back.

Phase 18 Step 3 and Step 5's baseline. The gold answers are Phase 12's
hand-written relations; this checks that `ask` returns each of them and
records which questions have no data yet.

    uv run python -m vault rdf
    uv run python -m tools.measure_phase18
"""

import re
import time
from collections import Counter
from pathlib import Path

from vault.ask import (
    PERSONAL,
    TECHNICAL,
    affected,
    crossing,
    evidence,
    lineage,
    review,
    together,
)
from vault.graph import in_graph
from vault.links import link_parts
from vault.rdf import build_graph, doc_iri, doc_path
from vault.scan import nfc, resolve_link, scan_vault

VAULT = Path.home() / (
    "Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault"
)
ANSWERS = Path(__file__).parent.parent / "docs/part3/gold-set-answers.md"
BLOCK = re.compile(r"\*\*`([^`]+)`\*\*[^\n]*\n\n```yaml\n(.*?)```", re.S)
ITEM = re.compile(r'^\s+-\s+"?(?:\[\[)?([^\]"]+?)(?:\]\])?"?\s*$', re.M)


def gold():
    """(document name, target) for every hand-written relation."""
    for name, body in BLOCK.findall(ANSWERS.read_text(encoding="utf-8")):
        for target in ITEM.findall(body):
            yield name, target


def main():
    graph = build_graph(VAULT)
    notes, index, targets = scan_vault(VAULT)
    inside = {note for note in notes if in_graph(note)}

    def node(name):
        landed = resolve_link(nfc(link_parts(name)[0]), index, targets)
        return doc_iri(landed) if landed in inside else None

    print(f"asserted graph  트리플 {len(graph):,}\n")

    print("gold answer 회귀 — 손으로 쓴 관계를 `ask evidence` 가 되찾는가")
    hit = miss = 0
    for name, target in gold():
        subject = node(name)
        if subject is None:
            continue
        answer = evidence(graph, subject)
        wanted = link_parts(target)[0].rsplit("/", 1)[-1]
        if any(
            wanted in hop.target or hop.target == target
            for path in answer.paths
            for hop in path
        ):
            hit += 1
        else:
            miss += 1
            print(f"   ✗ {name[:34]:36} → {target[:44]}")
    print(f"   {hit} 되찾음 · {miss} 놓침\n")

    print("질문별 결과")
    whole = {"review": review, "crossing": crossing, "together": together}
    for label, question in whole.items():
        start = time.perf_counter()
        answer = question(graph)
        print(
            f"   {label:12} {len(answer.paths):5} 경로  {answer.status:12}"
            f" {time.perf_counter() - start:5.2f}s"
        )

    print("\n문서별 질문 — 관계를 가진 문서 전부에")
    # A set: `subjects()` yields once per triple, so a document with 20
    # facts would be counted 20 times.
    subjects = {s for s in graph.subjects(None, None) if "#" not in str(s)}
    for label, question in (
        ("lineage", lineage),
        ("evidence", evidence),
        ("affected", affected),
    ):
        start = time.perf_counter()
        statuses = Counter(question(graph, s).status for s in subjects)
        print(f"   {label:12} {dict(statuses)}  {time.perf_counter() - start:5.2f}s")

    print("\n대역별 — 의미 관계를 가진 문서")
    bands = Counter(
        doc_path(str(s).partition("#")[0]).split("/", 1)[0]
        for s in subjects
        if evidence(graph, s).status != "unrecorded"
    )
    for band, n in bands.most_common():
        side = "개인" if band in PERSONAL else "기술" if band in TECHNICAL else "그 밖"
        print(f"   {n:5}  {band:26} {side}")


if __name__ == "__main__":
    main()
