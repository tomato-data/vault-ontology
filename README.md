# vault-ontology

Obsidian vault를 **기계가 읽는 그래프**로 만드는 도구를, 직접 짜면서 온톨로지를 배운다.

- **로드맵** → [`docs/README.md`](docs/README.md)
- **배운 것** → [`learnings/README.md`](learnings/README.md)
- **답안지** → `~/Desktop/Code/vault-cli/vault.py` (막힐 때만 연다)

```bash
uv run pytest -v          # 테스트
uv run python -m vault     # CLI (Phase 4부터)
```

| 디렉토리 | 소유 | 내용 |
|---|---|---|
| `docs/` | Claude | Phase 가이드. 무엇을 왜 만드는지 |
| `learnings/` | 토마토 | Q&A · 회고. 실제로 배운 것 |
| `vault/` | 토마토 | 손으로 짜는 코드 |
| `tests/` | 토마토 | TDD 테스트 |
