"""Blind judgement sheet: no model ranks, no v1-gold marks, deterministic shuffle.

Judging while the ranking is visible would let the model ordering steer the
labels — the thing the labels are supposed to grade. Order is hashed from the
stem so the sheet is reproducible without a random seed.
"""
import json, sys, pathlib, hashlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import logging; logging.getLogger("rdflib").setLevel(logging.CRITICAL)
from vault.frontmatter import split_frontmatter, fm_get

V = pathlib.Path(sys.argv[1]); lo, hi = int(sys.argv[2]), int(sys.argv[3])
pool = json.load(open("pool.json"))
for q in pool:
    if not (lo <= q["id"] <= hi): continue
    print(f"\n{'='*76}\nq{q['id']} [{q['cat']}]  {q['q']}")
    cands = sorted(q["pool"], key=lambda c: hashlib.md5(
        f"{q['id']}:{c['stem']}".encode()).hexdigest())
    for j, c in enumerate(cands, 1):
        fm, _ = split_frontmatter((V/c["doc"]).read_text(encoding="utf-8"))
        t = fm_get(fm, "type") or "?"
        s = (fm_get(fm, "summary") or "").strip()
        print(f"  {j:>2}. {c['stem'][:62]}")
        print(f"      {t:<11} {c['doc'].split('/')[0][:22]:<22} · {c['best_heading'][:40]}")
        if s: print(f"      → {s[:100]}")
