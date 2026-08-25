# 임베딩 모델 A/B — 실행 방법

> 무엇을 왜 하는지는 vault 의 `000 Index/Dots/집 PC 인계 — 임베딩 모델 A-B 시험.md`.
> 판단 근거는 `docs/retrieval-architecture.md`.

## 준비

```bash
cd experiments/ab
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python torch sentence-transformers numpy
```

## 실행

```bash
# 1) 청킹 — vault 를 읽어 chunks.json 생성 (약 1분)
uv run python chunk.py "$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault" chunks.json

# 2) 임베딩 — 4개 모델 순차 (M4 기준 약 5시간, M5 Pro 약 2.5시간)
./run_all.sh                 # 진행: tail -f prog_*.log

# 3) 평가 — 40 질의 × 4 모델
for M in "BAAI/bge-m3" "nlpai-lab/KURE-v1" \
         "Snowflake/snowflake-arctic-embed-l-v2.0" "dragonkue/snowflake-arctic-embed-l-v2.0-ko"; do
  ./.venv/bin/python eval.py "$M" chunks.json vecs queries.json results
done
```

## 고정된 설정 (네 모델에 동일)

| | |
|---|---|
| 청킹 | 헤딩 기반 → 문단 → 하드컷. 1,200자 상한 · 중첩 0 |
| 청크 접두 | 제목 + summary + 태그 (vault frontmatter) |
| 코퍼스 | 문서 3,857 → 청크 43,635 (캡 없음) |
| `max_seq_length` | 768 — 최장 청크가 767 토큰이라 **무손실** |
| 정밀도 | fp32. **fp16 금지** (MPS 데드락), bf16 은 이득 없음 |
| 배치 | 64 (32·128 보다 빠름, 실측) |
| 정규화 | L2 — 코사인이 내적이 된다 |

설정을 바꾸면 네 모델 전부 다시 돌려야 한다. 한 팔만 바꾸면 비교가 무효다.

## 측정된 함정 둘

- **fp16 (`.half()`) 은 MPS 에서 멈춘다.** `mps_copy_`/`copy_and_sync` 에서 데드락.
  22분간 CPU 0% 로 매달렸다. bf16 은 완주하지만 0.94x 로 더 느리다.
- **속도를 앞 구간에서 외삽하지 말 것.** sentence-transformers 는 긴 청크부터
  처리하므로 초반 10% 가 가장 느리다. 거기서 외삽하면 12.6시간이 나오는데
  무작위 표본 실측은 10 chunk/s = 약 5시간이다.
