"""Paired comparison on the v2 gold. recall@5 is ceiling-bound now, so read @10/@20."""
import json, math, sys
M = {"bge-m3":"BAAI__bge-m3", "KURE-v1":"nlpai-lab__KURE-v1",
     "arctic":"Snowflake__snowflake-arctic-embed-l-v2.0",
     "dragonkue-ko":"dragonkue__snowflake-arctic-embed-l-v2.0-ko"}
D = sys.argv[1] if len(sys.argv) > 1 else "results.v2"
R = {k: json.load(open(f"{D}/{v}.eval.json")) for k, v in M.items()}
CROSS = {"한→영", "영→한"}

def labels(m, mode):
    o = {}
    for r in R[m]["per_query"]:
        c = r["cat"] in CROSS
        if (mode == "cross" and not c) or (mode == "same" and c): continue
        for g, rank in r["gold_ranks"].items(): o[(r["id"], g)] = rank
    return o

def hits(m, k, mode):
    L = labels(m, mode)
    return {x for x in L if L[x] and L[x] <= k}, len(L)

def mcnemar(b, c):
    n = b + c
    if n == 0: return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2**n)

def pair(a, b, k, mode, name):
    ah, n = hits(a, k, mode); bh, _ = hits(b, k, mode)
    down, up = len(ah - bh), len(bh - ah)
    print(f"  {name:<26} {len(ah):>3}/{n} → {len(bh):>3}/{n}  ({len(bh)-len(ah):+3d})"
          f"  {down}↓/{up}↑  p={mcnemar(down, up):.3f}")

for mode, lab in [("cross","교차언어"), ("same","동일언어"), ("all","전체")]:
    print(f"\n=== {lab} (골드 {len(labels('bge-m3', mode))}개) ===")
    for k in (10, 20):
        print(f" recall@{k}")
        pair("bge-m3","KURE-v1", k, mode, "쌍1  bge-m3 → KURE-v1")
        pair("arctic","dragonkue-ko", k, mode, "쌍2  arctic → dragonkue-ko")

print("\n=== 순위 (전체) ===")
for k in (10, 20):
    row = sorted(((len(hits(m, k, "all")[0]), m) for m in M), reverse=True)
    n = hits("bge-m3", k, "all")[1]
    print(f" recall@{k:<3} " + " · ".join(f"{m} {c}/{n} ({c/n:.3f})" for c, m in row))
print("\n=== 교차언어만 ===")
for k in (10, 20):
    row = sorted(((len(hits(m, k, "cross")[0]), m) for m in M), reverse=True)
    n = hits("bge-m3", k, "cross")[1]
    print(f" recall@{k:<3} " + " · ".join(f"{m} {c}/{n} ({c/n:.3f})" for c, m in row))

print("\n=== dragonkue-ko 대 나머지 셋 (짝지어 비교) ===")
for other in ["arctic", "bge-m3", "KURE-v1"]:
    for k in (10, 20):
        pair(other, "dragonkue-ko", k, "all", f"{other} → dragonkue-ko @{k}")

print("\n=== 아무도 못 찾은 골드 (top-20 밖, 네 모델 전부) ===")
L = {m: labels(m, "all") for m in M}
keys = sorted(L["bge-m3"])
miss = [x for x in keys if all(not L[m][x] or L[m][x] > 20 for m in M)]
cat = {r["id"]: r["cat"] for r in R["bge-m3"]["per_query"]}
print(f"  {len(miss)}/{len(keys)}건")
for i, g in miss[:12]:
    print(f"   q{i:>2} [{cat[i]}] {g[:56]}   등수 {[L[m][(i,g)] or '>200' for m in M]}")
