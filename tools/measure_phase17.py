"""Compare three ways of answering the same question, and count coverage.

Phase 17 Step 4. The comparison is the point: if a walk at query time
answers what materialised inference answers, nothing gets materialised —
which is the conclusion Phase 9 reached and this rechecks with the
operating rules in place.

    uv run python -m tools.measure_phase17
"""

import time
from pathlib import Path

from vault.inference import close
from vault.rdf import V, build_graph, doc_path
from vault.rules import SEMANTIC, coverage, explain, genealogy, shared_ground

VAULT = Path.home() / (
    "Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault"
)
ONTOLOGY = Path(__file__).parent.parent / "vault-ontology.ttl"


def timed(label, work):
    start = time.perf_counter()
    result = work()
    print(f"  {label:34} {time.perf_counter() - start:6.2f}s   {result}")
    return result


def name(node):
    return doc_path(str(node).partition("#")[0]).rsplit("/", 1)[-1][:-3][:46]


def main():
    graph = build_graph(VAULT)
    print(f"asserted graph  트리플 {len(graph):,}\n")

    print("C02 — 이 결정의 근거가 된 tradeoff와 출처는 무엇인가")

    # 1. 원본 그래프에 한 홉만 묻는다.
    def one_hop():
        pairs = list(graph.subject_objects(V.derived_from))
        return f"{len(pairs)}쌍 — 중간 문서를 못 돌려준다"

    timed("① 원본 asserted 1홉 질의", one_hop)

    # 2. 질의 시점에 걸어 들어간다.
    def walk():
        subjects = {s for p in SEMANTIC for s in graph.subjects(p, None)}
        chains = [path for s in subjects for path in genealogy(graph, s)]
        deep = [path for path in chains if len(path) >= 2]
        return f"사슬 {len(chains)} · 2홉 이상 {len(deep)}"

    timed("② query-time 걷기", walk)

    # 3. 추론기로 물질화한 뒤 같은 것을 묻는다.
    def materialise():
        from rdflib import Graph

        closed = close(graph, Graph().parse(ONTOLOGY, format="turtle"), owl=True)
        pairs = list(closed.subject_objects(V.derived_from))
        return f"트리플 {len(closed):,} · derived_from {len(pairs)}"

    timed("③ OWL RL 물질화", materialise)

    print("\n② 가 돌려주는 2홉 사슬 (C02 의 답)")
    subjects = {s for p in SEMANTIC for s in graph.subjects(p, None)}
    deep = sorted(
        (path for s in subjects for path in genealogy(graph, s) if len(path) >= 2),
        key=lambda path: str(path[0][0]),
    )
    for path in deep[:8]:
        print("   " + "  →  ".join([name(path[0][0])] + [name(hop[2]) for hop in path]))
    if len(deep) > 8:
        print(f"   … {len(deep) - 8}개 더")

    print("\n설명 — 한 사슬을 펼치면")
    for line in explain(deep[0]):
        print("   " + line)

    print("\n규칙별 coverage")
    counts = coverage(graph)
    print(f"   genealogy 사슬 길이별  {counts['genealogy']}")
    print(f"   shared_ground 묶음     {counts['shared_ground']}")
    print(
        f"   invalidated            {counts['invalidated']}   ← 0 이면 데이터가 얇은 것"
    )

    print("\n같은 근거를 공유하는 것들 (C05·C06)")
    for source, users in shared_ground(graph)[:5]:
        print(f"   {name(source)[:40]:42} ← {len(users)}개")

    print("\n관계별 재료")
    for predicate in SEMANTIC:
        n = len(list(graph.subject_objects(predicate)))
        print(f"   {str(predicate).rsplit('/', 1)[-1]:16} {n}")


if __name__ == "__main__":
    main()
