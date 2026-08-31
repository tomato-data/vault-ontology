"""v1 gold + pooled judgements -> queries.v2.json, with the checks that matter.

v1 labels survive by default; the one exception is recorded in DROPPED with a
reason, because silently deleting a label would hide a judgement call inside a
number. Every label is checked against the corpus and against the trap.
"""
import json, glob, unicodedata
from pathlib import Path

DROPPED = {  # (query id, stem): why this v1 label is not relevant after all
    (24, "08-auth-account"):
        "세션 관리·토큰 만료(ASVS V3) 문서다. 「권한을 어떻게 나눴나」가 아니라 "
        "「권한 변경을 얼마나 빨리 반영하나」를 다룬다. 같은 풀에 03-authorization 이 있다.",
}

judged = {}
for f in sorted(glob.glob("judge/*.json")):
    judged.update(json.load(open(f)))

queries = json.load(open("queries.json"))
chunks = json.load(open("chunks.json"))
stems = {Path(c["doc"]).stem for c in chunks}

out, report = [], []
for q in queries:
    v1 = list(q["gold"])
    new = judged[str(q["id"])]
    merged, seen = [], set()
    for g in v1 + new:
        if (q["id"], g) in DROPPED or g in seen:
            continue
        seen.add(g); merged.append(g)
    o = {"id": q["id"], "cat": q["cat"], "q": q["q"], "gold": merged,
         "gold_v1": v1, "added": [g for g in merged if g not in v1]}
    if q.get("trap"):
        o["trap"] = q["trap"]
    out.append(o)
    report.append((q["id"], q["cat"], len(v1), len(merged)))

# --- 검사 ---
bad_stem = [(o["id"], g) for o in out for g in o["gold"] if g not in stems]
bad_norm = [(o["id"], g) for o in out for g in o["gold"]
            if unicodedata.normalize("NFC", g) != g]
trap_in_gold = [(o["id"], o["trap"]) for o in out
                if o.get("trap") and o["trap"] in o["gold"]]
dup = [(o["id"], g) for o in out for g in set(o["gold"]) if o["gold"].count(g) > 1]

print(f"{'q':>3} {'범주':<6} {'v1':>3} → {'v2':>3}")
for i, c, a, b in report:
    print(f"{i:>3} {c:<6} {a:>3} → {b:>3}   {'+' * (b - a)}")
print(f"\n골드 {sum(len(o['gold']) for o in out)}개 (v1 {sum(len(o['gold_v1']) for o in out)})")
print(f"  코퍼스에 없는 라벨 : {bad_stem or '없음'}")
print(f"  NFC 아닌 라벨      : {bad_norm or '없음'}")
print(f"  함정이 골드에 섞임 : {trap_in_gold or '없음'}")
print(f"  중복 라벨          : {dup or '없음'}")
print(f"  버린 v1 라벨       : {[k for k in DROPPED] or '없음'}")
json.dump(out, open("queries.v2.json", "w"), ensure_ascii=False, indent=1)
json.dump({f"{k[0]}:{k[1]}": v for k, v in DROPPED.items()},
          open("judge/dropped.json", "w"), ensure_ascii=False, indent=1)
