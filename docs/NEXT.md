# NEXT — Phase 1~9 종료 상태와 Phase 10 재개 지점

> Phase 1~9는 2026-08-25에 모두 끝났다. 그 결론은 변경하지 않는다.
> 같은 저장소에서 별도 목표의 3부를 시작하며, 다음 재개 지점은 Phase 10이다.

---

## 환경 복원 절차

```bash
git clone git@github.com:tomato-data/vault-ontology.git ~/Desktop/Code/vault-ontology
cd ~/Desktop/Code/vault-ontology
uv sync
uv run pytest -v          # 2026-08-25 기준 241개 통과해야 정상 출발점
```

### 답안지

`reference/`에 함께 들어 있다 (vault-cli `21faa91`, 2026-08-11 스냅샷). 별도로 받을 것이 없다.

**막히기 전에는 열지 않는다.** 자세한 사용 규칙은 [`reference/README.md`](../reference/README.md).
Phase 1~5까지만 답이 있고, **2부(RDF·추론)는 답안지가 없다.**

vault 경로는 두 Mac 모두 같다.

```
~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault
```

---

## 현재 위치

**Phase 1~9 완료. 테스트 241개 통과. Phase 10~19 계획 수립.**

| Phase | 내용 | 상태 |
|---|---|---|
| 1~4 | frontmatter · 위키링크 · 스캔 · lint | ✅ |
| 5 | SQLite 그래프 — **1부 종료** | ✅ |
| 6 | RDF 재모델링 | ✅ |
| 7 | SPARQL 질의 · SQLite 비교 | ✅ |
| 8 | RDFS/OWL/SKOS 어휘 설계 | ✅ |
| 9 | 추론 · 최종 판단 | ✅ |
| 10 | 문제 계약 · 역량 질문 20개 | 다음 시작점 |
| 11~19 | 의미 정체성 · 온톨로지 · 검증 · 추론 · 운영 | 계획 |

`vault/`에는 파서·검증·SQLite 그래프·RDF·SPARQL·추론 구현이 모두 들어 있다.
최종 결론은 [`../learnings/verdict.md`](../learnings/verdict.md)에 있다.

### 2부에서 확인한 것

같은 질문을 재귀 CTE, SPARQL property path, 추론기로 각각 풀었다. SPARQL은
이행 폐쇄와 역방향 순회를 간결하게 표현했지만, 이 vault에서 SQLite로 답하지
못한 질의는 없었다. OWL RL 물질화는 16.6초가 걸렸고 트리플 수를 2.81배로
늘렸지만, 질적으로 새로운 유용한 사실은 만들지 못했다.

### 이 프로젝트가 무엇인가

파서 재구현 연습이 아니라 **내 vault를 강화하는 작업**이다.
`reference/`와 스키마 정본은 **권위가 아니라 검토 대상**이다.

Phase 4에서 그 간극이 **코드의 우위**로 나타났고(답안지가 못 보는 24건),
Phase 6에서는 **사람이 코드를 이겼다** — 「왜 형제 파일이 `part_of`인가」라는
질문 하나가 답안지에서 물려받아 새 모델까지 실려온 설계 오류를 잡았다.

### 최종 결정

| 판단 | 결정 |
|---|---|
| 상시 운용 | **SQLite 구현을 사용한다** |
| RDF 산출물 | 상호운용과 학습용으로 남긴다 |
| rdflib 상시 운용(v1) | 진행하지 않는다 |
| Oxigraph(v2) | 성능이 아니라 추가 학습 목적이 생길 때 재검토한다 |
| 문서 유형 계층 | Content·Imported·Structural의 3역할 계층만 채택한다 |
| vault·800 TRPG 병합 | 두 코퍼스를 함께 물어야 하는 질의가 생길 때까지 미룬다 |

전체 근거는 [`../learnings/verdict.md`](../learnings/verdict.md)에 있으며,
IRI 결정의 세부 내용은 [`iri-policy.md`](iri-policy.md)에서 확인할 수 있다.

### 여기까지 오면서 확정한 것

| 결정 | 근거 |
|---|---|
| 부재는 `fm_get` → `None`, `fm_list` → `[]` | 리스트는 "비어 있음 = 없음" |
| **RDF에는 NULL이 없다** | 값이 없으면 **트리플을 안 쓴다.** 열린 세계 가정의 시작 |
| 정규화는 **경계에서 한 번만** | 링크 5,341개(21.9%)가 여기 걸려 있다 |
| 「가깝다」 = **소스와 같은 폴더** | 넓히면 1,443개가 틀린 곳으로 간다 |
| **읽을 문서 ≠ 링크 대상** | 합치면 이미지 임베드 582건을 깨진 링크로 잘못 분류한다 |
| lint 제외는 **커밋되는 설정 파일**에 | 무엇을 왜 뺐는지가 감사 대상 |
| `main`은 정수를 돌려주고 `sys.exit`은 파일 끝 한 줄에만 | 프로세스 없이 테스트한다 |
| **바뀔 것을 이음매 하나에 가둔다** | `doc_iri`(정체성) · `resolve` 인자(해석) |
| 「있는가」가 아니라 **「결과가 달라지는가」**를 잰다 | 펜스 혼용 10건, 파싱 차이 0 |

### Phase 6 실측 (2026-08-24)

```
uv run python -m vault lint        # 382 위반
uv run python -m vault build       # SQLite
uv run python -m vault rdf         # .vault.ttl
```

| | SQLite | RDF | |
|---|---:|---:|---|
| 문서 | 3,993 | **3,993** | ✅ |
| `builds_on` / `supersedes` | 415 / 5 | **415 / 5** | ✅ |
| 태그 | 3,352 | **3,352** | ✅ |
| `links_to` | 10,622 | 9,359 | 집합이라 중복 1,162건이 하나로 합쳐진다 |
| `part_of` | 1,020 | 4,758 | 폴더가 리소스가 됐다 |
| **합계** | 엣지 12,057 | **트리플 27,515개** | |

추론 전 데이터 27,529개와 온톨로지 58개를 합친 뒤 OWL RL 추론을 돌리면
77,478개로 늘어난다(2.81배, 16.6초). 이 가운데 `rdfs:Resource`와 `owl:Thing`
14,656개는 실제 질의에 도움이 되지 않는 일반 타입 정보다.

> **`800 TRPG`가 2026-08-23에 vault 밖으로 나갔다** — [`800-trpg-split.md`](800-trpg-split.md).
> Phase 6·9의 실습 대상이 「제외 구역」에서 **「출처가 다른 독립 코퍼스」**로 바뀌었고,
> 문제가 약해진 게 아니라 **RDF가 원래 풀려던 문제**가 됐다.

---

## 다음 시작점 — 3부 Phase 10

2부의 "검색을 위해 온톨로지를 더 쌓지 않는다"는 결론을 유지한다. 3부는 검색 개선이
아니라 문서 안의 주장·사건·결정·원칙과 그 근거를 모델링하여 실제 역량 질문에 답하는
별도 목표다. 범위는 개발 지식에 한정하지 않고 개인 경험·성찰·철학·커리어·생활을
포함한 Vault 전체다. Phase 10은 000~700·900 대역별 질문과 영역 사이를 잇는 질문을
함께 고정하는 데서 시작한다. 현재 그래프에서 제외된 900 Archive는 현재 지식과
분리된 read-only/archive 경계로 참여시키는 방식을 먼저 결정한다.

진행 순서는 [`README.md`](README.md)의 3부 표와 각 Phase 가이드를 따른다.

1. [`phase10.md`](phase10.md) — 역량 질문·비목표·위험 장부
2. [`phase11.md`](phase11.md) — 문서와 지식 개체 분리, 안정 ID
3. [`phase12.md`](phase12.md) — 핵심 도메인 온톨로지 0.1
4. [`phase13.md`](phase13.md) — 의미 작성 계약과 gold set 50개
5. [`phase14.md`](phase14.md) — asserted/proposed/inferred 그래프
6. [`phase15.md`](phase15.md) — SHACL 의미 계약
7. [`phase16.md`](phase16.md) — 목적 제한 추론과 철회 가능한 운영 규칙
8. [`phase17.md`](phase17.md) — 의미 질의와 근거 설명
9. [`phase18.md`](phase18.md) — 제안·승인·철회 workflow
10. [`phase19.md`](phase19.md) — shadow mode를 거친 제한 운영

### Phase 10 전에 하지 않을 것

- 새 클래스와 OWL 공리부터 추가하지 않는다.
- 현재 `v:Concept`·`v:Principle`을 실제 개념·원칙 의미로 바꾸지 않는다.
- VectorDB 구현을 이 로드맵에 섞지 않는다.
- RDF 저장 엔진을 교체하지 않는다.
- 전체 Vault 자동 의미 추출을 시작하지 않는다.
- 에이전트 쓰기 권한을 붙이지 않는다.

### 병행하지만 별도인 운영 개선

- 생성 계열 명령 이관: [`cli-roadmap.md`](cli-roadmap.md)
- vault 운영 백로그: [`vault-backlog.md`](vault-backlog.md)
- 스키마 정본에 3역할 계층과 최종 결론 반영
- 실제로 두 코퍼스를 함께 물어야 하는 질의가 생기면 RDF 병합 재검토
- VectorDB·임베딩 검색: [`retrieval-architecture.md`](retrieval-architecture.md). 3부에서는
  `chunk_id → artifact IRI → knowledge entity` 연결 계약만 다룬다

---

## 커밋 규칙 (Conventional Commits)

**기본은 하나로 담는다.** 구현 · 테스트 · `learnings/` · 문서 갱신까지 커밋 하나.
Step 하나가 곧 커밋 하나다. 잘게 쪼개면 이력이 오히려 안 읽힌다.

| 시점 | type | 예 |
|---|---|---|
| GREEN (구현·테스트·학습노트 함께) | `feat` | `feat(frontmatter): fm_list — 리스트 블록 파싱` |
| 실측 (스크립트·결과·회고 함께) | `feat(tools)` | `feat(tools): Phase 1 파서 실측` |
| REFACTOR | `refactor` | `refactor(frontmatter): 키 매칭 정규식을 헬퍼로 추출` |
| 기존 동작이 틀렸던 것 | `fix` | `fix(links): 표 안의 \|가 타깃 끝에 역슬래시를 남기던 문제` |
| **코드가 안 바뀐 때만** | `docs` | `docs: Phase 2 가이드 — 위키링크 파서` |

- RED는 커밋하지 않는다 — 실패 상태가 이력에 남으면 `git bisect`를 못 쓴다. GREEN 커밋에 테스트가 같이 들어가므로 명세는 보존된다
- GREEN과 REFACTOR를 **한 커밋에 섞지 않는다.** 섞으면 diff에서 "기능이 바뀐 건가 정리한 건가"를 읽을 수 없다
- 메시지는 **영어로, 제목 한 줄 + 불릿 2~3개.** 길게 쓰지 않는다. 함정과 설계 결정의 상세는 `learnings/`가 맡는다
- `Co-Authored-By` 트레일러는 쓰지 않는다

### scope

| Phase | scope |
|---|---|
| 1 | `frontmatter` |
| 2 | `links` |
| 3 | `scan` |
| 4 | `lint` |
| 5 | `graph` |
| 6 | `rdf` |
| 7 | `sparql` |
| 8 | `vocab` |
| 9 | `inference` |
| 10 | `questions` |
| 11 | `identity` |
| 12 | `domain-vocab` |
| 13 | `annotation` |
| 14 | `semantic-graph` |
| 15 | `shacl` |
| 16 | `rules` |
| 17 | `semantic-query` |
| 18 | `proposal` |
| 19 | `operations` |

---

## 진행 방식 요약

```
RED       테스트를 쓴다 → 실패를 눈으로 확인
GREEN     최소 구현 → 통과 → 커밋
REFACTOR  개선점 검토 (없으면 "없다"고 판단하는 것도 결과) → 있으면 별도 커밋
실측       실제 vault에 돌려 답안지 출력과 대조
```

**단위 테스트가 전부 초록이어도 실제 데이터에서 숫자가 다르면 틀린 것이다.**
