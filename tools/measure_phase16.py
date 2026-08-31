"""Time SHACL at three sizes and check parity with Python lint.

Phase 16 Step 5. Engine replacement is considered only after a real
bottleneck shows up here, so the point is the number and not the verdict.

    uv run python -m tools.measure_phase16
"""

import re
import time
from collections import Counter
from pathlib import Path

from rdflib import Graph
from rdflib.namespace import RDF

from vault.graph import in_graph
from vault.lint import lint_vault
from vault.rdf import V, build_graph, doc_iri
from vault.scan import scan_vault
from vault.shacl import findings, shapes_graph

VAULT = Path.home() / (
    "Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault"
)
GOLD = Path(__file__).parent.parent / "docs/part3/gold-set-manifest.md"


def subgraph(whole, paths):
    """Every triple whose subject is one of `paths` or a section of one.

    Sliced by subject, because a shape targets a focus node. Slicing by
    object as well would drag half the vault in behind a single link.
    """
    wanted = {str(doc_iri(path)) for path in paths}
    part = Graph()
    for subject, predicate, obj in whole:
        head = str(subject).partition("#")[0]
        if head in wanted:
            part.add((subject, predicate, obj))
    return part


def gold_paths():
    """The 50 documents Phase 12 labelled by hand."""
    # `| 1 | `principle` | `000 Index/…/400 Logic Forge.md` | 메타 원칙 …`
    # The path is the third cell and always backticked.
    rows = re.findall(
        r"^\|[^|]+\|[^|]+\|\s*`([^`]+\.md)`", GOLD.read_text(encoding="utf-8"), re.M
    )
    return rows


def run(label, data, shapes):
    start = time.perf_counter()
    _, found = findings(data, shapes)
    elapsed = time.perf_counter() - start
    counts = Counter(f["severity"] for f in found)
    print(
        f"{label:24} 트리플 {len(data):7,}  {elapsed:6.2f}s   "
        f"violation {counts.get('violation', 0):4} · warning {counts.get('warning', 0):4}"
    )
    return found


def main():
    shapes = shapes_graph()
    whole = build_graph(VAULT)
    notes, _, _ = scan_vault(VAULT)
    inside = [note for note in notes if in_graph(note)]

    gold = [p for p in gold_paths() if p in set(inside)]
    print(f"gold set manifest 에서 읽은 경로 {len(gold)}개\n")

    run("gold set 50", subgraph(whole, gold), shapes)
    run("확대 표본 500", subgraph(whole, sorted(inside)[:500]), shapes)
    found = run("전체 vault", whole, shapes)

    print("\nshape 별 분포")
    for shape, n in Counter(f["shape"].rsplit("/", 1)[-1] for f in found).most_common():
        name = shape if not shape.startswith("N") else "JudgementNeedsSummary"
        print(f"   {n:5}  {name}")

    print("\n모집단 — 아무것도 안 세는 shape 를 잡기 위해")
    for label, class_ in (
        ("PrincipleDocument", V.PrincipleDocument),
        ("DecisionDocument", V.DecisionDocument),
    ):
        print(f"   {len(set(whole.subjects(RDF.type, class_))):5}  {label}")

    print("\nparity — 판단 구간의 summary")
    shacl = sum(1 for f in found if "summary" in f["message"])
    python = sum(1 for _, code, _ in lint_vault(VAULT) if code == "summary missing")
    print(
        f"   SHACL {shacl} · Python lint {python} · {'일치' if shacl == python else '어긋남'}"
    )


if __name__ == "__main__":
    main()
