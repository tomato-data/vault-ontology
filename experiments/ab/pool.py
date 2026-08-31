"""Build the judgement pool: union of every model's top-K documents per query.

Standard TREC-style pooling. The gold set was written from memory and turned out
to name 2 documents where the vault holds five equally good ones, so absolute
recall was floored by the labels, not by the models. Pooling fixes that for the
systems in the pool — and only for those. A document no model retrieved cannot
enter the pool, so this inflates absolute recall and stays fair only between the
four arms that contributed. That bias is the price and it must be reported.
"""
import json, sys, warnings
from pathlib import Path
warnings.filterwarnings("ignore")
import numpy as np
from sentence_transformers import SentenceTransformer

MODELS = ["BAAI/bge-m3", "nlpai-lab/KURE-v1",
          "Snowflake/snowflake-arctic-embed-l-v2.0",
          "dragonkue/snowflake-arctic-embed-l-v2.0-ko"]
DEPTH = 10

def main(chunks_path, vec_dir, queries_path, out_path):
    chunks = json.load(open(chunks_path))
    queries = json.load(open(queries_path))
    stems = np.array([Path(c["doc"]).stem for c in chunks])
    docs  = np.array([c["doc"] for c in chunks])
    heads = np.array([c["heading"] for c in chunks])

    pool = {q["id"]: {} for q in queries}
    for mid in MODELS:
        slug = mid.replace("/", "__")
        vecs = np.load(Path(vec_dir) / f"{slug}.npy")
        model = SentenceTransformer(mid, device="mps")
        model.max_seq_length = json.load(open(Path(vec_dir)/f"{slug}.meta.json"))["max_seq_length"]
        qv = model.encode([q["q"] for q in queries], convert_to_numpy=True,
                          normalize_embeddings=True).astype(np.float32)
        for q, v in zip(queries, qv):
            scores = vecs @ v
            best = {}
            for i in np.argsort(-scores):
                s = stems[i]
                if s not in best:
                    best[s] = (float(scores[i]), docs[i], heads[i])
                    if len(best) >= DEPTH:
                        break
            for rank, (s, (sc, doc, head)) in enumerate(
                    sorted(best.items(), key=lambda kv: -kv[1][0]), 1):
                e = pool[q["id"]].setdefault(
                    s, {"doc": str(doc), "best_heading": str(head), "ranks": {}})
                e["ranks"][mid] = rank
        del model, vecs
        print(f"  pooled {mid}", file=sys.stderr)

    out = []
    for q in queries:
        cands = pool[q["id"]]
        out.append({"id": q["id"], "cat": q["cat"], "q": q["q"],
                    "gold_v1": q["gold"], "trap": q.get("trap"),
                    "pool": [{"stem": s, **v} for s, v in
                             sorted(cands.items(), key=lambda kv: min(kv[1]["ranks"].values()))]})
    json.dump(out, open(out_path, "w"), ensure_ascii=False, indent=1)
    sizes = [len(o["pool"]) for o in out]
    print(f"풀 {sum(sizes)}건 · 질의당 평균 {sum(sizes)/len(sizes):.1f} · 최대 {max(sizes)} · 최소 {min(sizes)}")

if __name__ == "__main__":
    main(*sys.argv[1:5])
