"""Embed the fixed chunk set with one model. Every run records its own settings."""
import json, sys, time, platform
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer

def main(model_id, chunks_path, out_dir, batch=64):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    slug = model_id.replace("/", "__")
    chunks = json.load(open(chunks_path))
    texts = [c["text"] for c in chunks]

    t0 = time.perf_counter()
    model = SentenceTransformer(model_id, device="mps")
    model.max_seq_length = 768      # chunks top out at 767 tokens — nothing is truncated
    # NO .half(): fp16 on MPS deadlocks in mps_copy_/copy_and_sync when the
    # result is pulled back with .cpu(). Measured: hung 22 min at 0% CPU.
    load_s = time.perf_counter() - t0

    t1 = time.perf_counter()
    vecs = model.encode(
        texts, batch_size=batch, convert_to_numpy=True,
        normalize_embeddings=True,      # cosine becomes a dot product
        show_progress_bar=True,
    ).astype(np.float32)
    encode_s = time.perf_counter() - t1

    np.save(out / f"{slug}.npy", vecs)
    meta = {
        "model_id": model_id,
        "dim": int(vecs.shape[1]),
        "chunks": int(vecs.shape[0]),
        "max_seq_length": int(model.max_seq_length),
        "precision": "fp32",
        "normalized": True,
        "dtype": "float32",
        "batch_size": batch,
        "device": "mps",
        "load_seconds": round(load_s, 1),
        "encode_seconds": round(encode_s, 1),
        "chunks_per_second": round(len(texts) / encode_s, 1),
        "vector_mb": round(vecs.nbytes / 1024 / 1024, 1),
        "platform": platform.platform(),
    }
    json.dump(meta, open(out / f"{slug}.meta.json", "w"), ensure_ascii=False, indent=2)
    print(json.dumps(meta, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
