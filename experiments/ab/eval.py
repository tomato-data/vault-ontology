"""Score one model against the fixed query set.

A smoke test, not a benchmark. n=20 gives SE ~0.11, so only gaps of roughly
20 points are signal. Per-category n is 3-5 and cannot decide anything on its
own — the aggregate that matters is CROSS-LINGUAL (n=8), which is what the
whole set was built to probe: did Korean fine-tuning erode ko<->en alignment?

Retrieval is over chunks, gold labels are DOCUMENTS, so a document scores as
its best chunk (max pooling). Every gold document's rank is recorded, not just
the first, so the raw ordering can be re-read later.
"""
import json, sys, time
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer

CROSS = {"한→영", "영→한"}          # the question this set exists to answer

def main(model_id, chunks_path, vec_dir, queries_path, out_dir):
    slug = model_id.replace("/", "__")
    chunks = json.load(open(chunks_path))
    vecs = np.load(Path(vec_dir) / f"{slug}.npy")
    queries = json.load(open(queries_path))
    stems = np.array([Path(c["doc"]).stem for c in chunks])
    meta = json.load(open(Path(vec_dir) / f"{slug}.meta.json"))

    model = SentenceTransformer(model_id, device="mps")
    model.max_seq_length = meta["max_seq_length"]
    t0 = time.perf_counter()
    qv = model.encode([q["q"] for q in queries], convert_to_numpy=True,
                      normalize_embeddings=True).astype(np.float32)
    q_ms = (time.perf_counter() - t0) * 1000 / len(queries)

    rows, search_ms = [], []
    for q, v in zip(queries, qv):
        t = time.perf_counter()
        scores = vecs @ v
        best = {}
        for i in np.argsort(-scores):
            s = stems[i]
            if s not in best:
                best[s] = float(scores[i])
                if len(best) >= 200:      # deep enough to rank every gold
                    break
        names = [n for n, _ in sorted(best.items(), key=lambda kv: -kv[1])]
        search_ms.append((time.perf_counter() - t) * 1000)

        ranks = {g: (names.index(g) + 1 if g in names else None) for g in q["gold"]}
        hit = [r for r in ranks.values() if r]
        rows.append({
            "id": q["id"], "cat": q["cat"], "q": q["q"],
            "gold_ranks": ranks,                       # every gold, to the position
            "n_gold": len(q["gold"]),
            "hit5": sum(1 for r in hit if r <= 5),
            "hit10": sum(1 for r in hit if r <= 10),
            "first_rank": min(hit) if hit else None,
            "rr": 1.0 / min(hit) if hit else 0.0,
            "top5": names[:5],
            # trap: does the same-word, different-meaning note outrank the gold?
            "trap": q.get("trap"),
            "trap_rank": (names.index(q["trap"]) + 1) if q.get("trap") in names else None,
        })

    def agg(sel):
        if not sel: return None
        return {"n": len(sel),
                "recall@5": round(sum(r["hit5"] for r in sel) / sum(r["n_gold"] for r in sel), 3),
                "recall@10": round(sum(r["hit10"] for r in sel) / sum(r["n_gold"] for r in sel), 3),
                "mrr": round(sum(r["rr"] for r in sel) / len(sel), 3)}

    traps = [r for r in rows if r["trap"]]
    trap_beaten = sum(1 for r in traps
                      if r["trap_rank"] and r["first_rank"] and r["trap_rank"] < r["first_rank"])
    cats = sorted({r["cat"] for r in rows})
    result = {
        "model_id": model_id,
        "embedding_settings": meta,
        "chunking": json.load(open(Path(chunks_path).parent / "chunking.json")),
        "overall": agg(rows),
        "cross_lingual": agg([r for r in rows if r["cat"] in CROSS]),        # n=8, the real question
        "same_lingual": agg([r for r in rows if r["cat"] not in CROSS]),     # n=12
        "by_category_UNDERPOWERED": {c: agg([r for r in rows if r["cat"] == c]) for c in cats},
        "trap": {"n": len(traps), "trap_outranked_gold": trap_beaten,
                 "gold_at_rank1": sum(1 for r in traps if r["first_rank"] == 1)},
        "query_encode_ms_avg": round(q_ms, 1),
        "search_ms_median": round(sorted(search_ms)[len(search_ms)//2], 2),
        "per_query": rows,
    }
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    json.dump(result, open(Path(out_dir) / f"{slug}.eval.json", "w"), ensure_ascii=False, indent=2)
    print(f"{model_id}")
    print(f"  overall        {result['overall']}")
    print(f"  cross_lingual  {result['cross_lingual']}   ← 핵심")
    print(f"  same_lingual   {result['same_lingual']}")
    print(f"  trap           {result['trap']}")

if __name__ == "__main__":
    main(*sys.argv[1:6])
