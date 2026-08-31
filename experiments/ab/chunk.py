"""Chunk the vault. Identical output feeds every model, so only the model varies.

Heading-based: a markdown heading is an author-made boundary, so splitting there
beats a fixed window. Each chunk carries the note title, summary and tags as a
prefix — the vault already has that metadata, and it is the cheap stand-in for
Anthropic-style contextual retrieval.
"""
import json, pathlib, re, sys
from pathlib import Path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))  # repo root — derived, not hardcoded
import logging; logging.getLogger("rdflib").setLevel(logging.CRITICAL)
from vault.scan import scan_vault
from vault.frontmatter import split_frontmatter, fm_get, fm_list
from vault.graph import in_graph

MAX_CHARS = 1200      # ~500 tokens for mixed KR/EN
MIN_CHARS = 80        # below this, fold into the neighbour

def split_by_heading(body):
    """Yield (heading_path, text) at the deepest heading that still has text."""
    lines = body.split("\n")
    stack, buf, out = [], [], []
    def flush():
        text = "\n".join(buf).strip()
        if text:
            out.append((" > ".join(stack), text))
    for line in lines:
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            flush(); buf = []
            depth = len(m.group(1))
            stack = stack[:depth-1] + [m.group(2).strip()]
        else:
            buf.append(line)
    flush()
    return out

def window(text, size=MAX_CHARS):
    """Split an over-long section on paragraph breaks, never mid-sentence.

    A section with no paragraph breaks — a long table, a code block, a worklog —
    would otherwise stay whole and be silently truncated by the model's max
    sequence length. So every piece gets a hard character cut as a backstop.
    """
    if len(text) <= size:
        return [text]
    parts, cur = [], []
    for para in text.split("\n\n"):
        if sum(len(p) for p in cur) + len(para) > size and cur:
            parts.append("\n\n".join(cur)); cur = []
        cur.append(para)
    if cur: parts.append("\n\n".join(cur))
    # backstop: nothing leaves here longer than `size`
    out = []
    for part in parts:
        while len(part) > size:
            cut = part.rfind("\n", 0, size)
            if cut < size // 2:
                cut = size
            out.append(part[:cut]); part = part[cut:].lstrip("\n")
        if part:
            out.append(part)
    return out

def main(vault_dir, out_path):
    V = Path(vault_dir)
    notes, _, _ = scan_vault(V)
    chunks = []
    for rel in sorted(notes):
        if not in_graph(rel):
            continue
        fm, body = split_frontmatter((V/rel).read_text(encoding="utf-8"))
        title = Path(rel).stem
        summary = fm_get(fm, "summary") or ""
        tags = " ".join(fm_list(fm, "tags"))
        # the metadata prefix every chunk of this note carries
        head = f"{title}\n{summary}\n{tags}".strip()
        sections = split_by_heading(body) or [("", body)]
        pending = ""
        for hpath, text in sections:
            for piece in window(text):
                piece = (pending + "\n" + piece).strip() if pending else piece.strip()
                pending = ""
                if len(piece) < MIN_CHARS:
                    pending = piece
                    continue
                chunks.append({
                    "doc": rel,
                    "title": title,
                    "heading": hpath,
                    "text": f"{head}\n\n{hpath}\n{piece}".strip(),
                })
        if pending and chunks and chunks[-1]["doc"] == rel:
            chunks[-1]["text"] += "\n" + pending
    json.dump(chunks, open(out_path, "w"), ensure_ascii=False)
    docs = len({c["doc"] for c in chunks})
    lens = sorted(len(c["text"]) for c in chunks)
    print(f"문서 {docs} → 청크 {len(chunks)}")
    print(f"  청크/문서 평균 {len(chunks)/docs:.1f}")
    print(f"  길이 중앙값 {lens[len(lens)//2]} · 최대 {lens[-1]} · 최소 {lens[0]}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
