import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import logging; logging.getLogger("rdflib").setLevel(logging.CRITICAL)
from vault.frontmatter import split_frontmatter, fm_get, fm_list
V = pathlib.Path(sys.argv[1]); lo, hi = int(sys.argv[2]), int(sys.argv[3])
pool = json.load(open("pool.json"))
for q in pool:
    if not (lo <= q["id"] <= hi): continue
    print(f"\n{'='*78}\nq{q['id']} [{q['cat']}]  {q['q']}")
    print(f"  v1 골드: {q['gold_v1']}" + (f"  · 함정: {q['trap']}" if q["trap"] else ""))
    for c in q["pool"]:
        fm, _ = split_frontmatter((V/c["doc"]).read_text(encoding="utf-8"))
        t = fm_get(fm, "type") or "?"
        s = (fm_get(fm, "summary") or "").strip()
        zone = c["doc"].split("/")[0]
        mark = "★" if c["stem"] in q["gold_v1"] else ("⚠" if c["stem"] == q["trap"] else " ")
        r = c["ranks"]; rs = "/".join(str(r.get(m, "-")) for m in
            ["BAAI/bge-m3","nlpai-lab/KURE-v1","Snowflake/snowflake-arctic-embed-l-v2.0","dragonkue/snowflake-arctic-embed-l-v2.0-ko"])
        print(f" {mark}[{rs:>12}] {c['stem'][:58]}")
        print(f"      {t:<12} {zone:<24} · {c['best_heading'][:44]}")
        if s: print(f"      → {s[:96]}")
