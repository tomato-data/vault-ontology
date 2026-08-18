# vault-ontology

Obsidian vault 6,452개 문서를 **기계가 읽는 그래프**로 만드는 도구를, 직접 짜면서 온톨로지를 배운다.

기존 도구 `vault-cli`는 이미 동작한다. 이 저장소는 그걸 **백지에서 다시 짜고**, 같은 데이터를 **RDF로 두 번째 모델링**해서 「지식 그래프」와 「온톨로지」의 차이를 손으로 확인하는 학습 프로젝트다.

```
Phase 1~5   파서 → 검증 → SQLite 그래프        속성 그래프 (답안지 있음)
Phase 6~9   RDF → SPARQL → RDFS/OWL → 추론     온톨로지 (답안지 없음)
```

## 시작

```bash
uv sync
uv run pytest -v
```

| 문서 | 내용 |
|---|---|
| **[docs/NEXT.md](docs/NEXT.md)** | **지금 어디고 다음이 뭔지. 재개할 때 여기부터** |
| [docs/README.md](docs/README.md) | 전체 로드맵 · 대조본 수치 · 성공 기준 |
| [docs/phase01.md](docs/phase01.md) ~ [phase09.md](docs/phase09.md) | Phase별 가이드 |
| [learnings/](learnings/) | Q&A · 회고 |
| [reference/](reference/) | 답안지 — 막히기 전에는 열지 않는다 |

## 구조

| 디렉토리 | 내용 |
|---|---|
| `docs/` | Phase 가이드. 무엇을 왜 만드는지 |
| `learnings/` | Q&A · 회고. 실제로 배운 것 |
| `vault/` | 코드 |
| `tests/` | TDD 테스트 |
| `reference/` | **답안지.** 기존 `vault-cli`의 고정 스냅샷 (`21faa91`, 2026-08-11) |

`reference/`는 Claude가 짠 기존 도구를 **회귀 대조본으로 고정해둔 것**이다. Phase 5에서 같은 vault에 둘 다 돌려 숫자가 일치하는지 확인한다. **Phase 6~9(RDF·추론)에는 답안지가 없다** — 그쪽 대조본은 Phase 5에서 내가 만든 SQLite 그래프다.

## 진행 방식

```
RED       테스트를 쓴다 → 실패를 눈으로 확인
GREEN     최소 구현 → 통과 → 커밋
REFACTOR  개선점 검토 → 있으면 별도 커밋
실측       실제 vault에 돌려 답안지 출력과 대조
```

단위 테스트가 전부 초록이어도 **실제 데이터에서 숫자가 다르면 틀린 것이다.**
