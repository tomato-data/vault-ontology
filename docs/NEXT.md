# NEXT — 지금 여기서 이어서 한다

> **다른 PC에서 재개할 때 이 파일부터 읽는다.**
> Step을 하나 끝낼 때마다 이 파일의 「현재 위치」와 「바로 다음」을 갱신한다.

---

## 재개 절차

```bash
git clone git@github.com:tomato-data/vault-ontology.git ~/Desktop/Code/vault-ontology
cd ~/Desktop/Code/vault-ontology
uv sync
uv run pytest -v          # 통과해야 정상 출발점
```

### 답안지

`reference/` 에 함께 들어 있다 (vault-cli `21faa91`, 2026-08-11 스냅샷). 별도로 받을 것이 없다.

**막히기 전에는 열지 않는다.** 자세한 사용 규칙은 [`reference/README.md`](../reference/README.md).
Phase 1~5까지만 답이 있고, **2부(RDF·추론)는 답안지가 없다.**

vault 경로는 두 Mac 모두 같다.

```
~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault
```

---

## 현재 위치

**Phase 7 (SPARQL) · Step 1 — RED 작성 직전**

Phase 1~6 완료. 테스트 199개 통과.

| Phase | 내용 | 상태 |
|---|---|---|
| 1~4 | frontmatter · 위키링크 · 스캔 · lint | ✅ |
| 5 | SQLite 그래프 — **1부 종료** | ✅ |
| 6 | RDF 재모델링 — 27,515 트리플 | ✅ |
| **7** | **SPARQL 질의** | **⬜ 여기부터** |
| 8~9 | 어휘 설계 · 추론 | ⬜ |

`vault/` 에 `frontmatter` · `links` · `scan` · `schema` · `lint` · `graph` · `rdf` ·
`__main__` 이 있다. Phase 7은 **새 모듈** `sparql.py`.

### 2부는 개념이 목적이다

1부는 구현이 목적이었고 개념이 따라왔다. **2부는 반대다.**
Phase 6 Step 1 이 코드가 아니라 IRI 정책 결정이었던 것도 그래서다.

**같은 질문을 세 번 푼다.** 재귀 CTE(끝남) → SPARQL property path → 추론기.
**답이 같아야 하고 표현력이 달라야 한다. 그 차이가 곧 온톨로지의 정의다.**

### 이 프로젝트가 무엇인가

파서 재구현 연습이 아니라 **내 vault 를 강화하는 작업**이다.
`reference/` 와 스키마 정본은 **권위가 아니라 검토 대상**이다.

Phase 4 에서 그 간극이 **코드의 우위**로 나타났고 (답안지가 못 보는 24건),
Phase 6 에서는 **사람이 코드를 이겼다** — 「왜 형제 파일이 `part_of` 인가」라는
질문 하나가 답안지에서 물려받아 새 모델까지 실려온 설계 오류를 잡았다.

### Phase 6 이 남긴 판단 넷

| 판단 | 결정 | 근거 |
|---|---|---|
| IRI 기준 | **경로.** 이음매는 `doc_iri` 하나 | 재빌드 밖에서 IRI 를 붙잡는 게 아직 없다 |
| 미해결 링크 | **`_raw` 리터럴** | IRI 를 만들면 `rdfs:range` 가 유령 357개를 Document 로 |
| `part_of` 대상 | **폴더 리소스** | 968/1,020 이 형제를 가리키고 있었다 |
| 태그 | **리소스 · `skos:broader`** | `Stack` 은 어느 문서에도 없는데 945개를 찾아준다 |

근거 전문은 [`iri-policy.md`](iri-policy.md) 와
[`learnings/phase06-qa.md`](../learnings/phase06-qa.md).

### 여기까지 오면서 확정한 것

| 결정 | 근거 |
|---|---|
| 부재는 `fm_get` → `None`, `fm_list` → `[]` | 리스트는 "비어 있음 = 없음" |
| **RDF 에는 NULL 이 없다** | 값이 없으면 **트리플을 안 쓴다.** 열린 세계 가정의 시작 |
| 정규화는 **경계에서 한 번만** | 링크 5,341개(21.9%)가 여기 걸려 있다 |
| 「가깝다」 = **소스와 같은 폴더** | 넓히면 1,443개가 틀린 곳으로 간다 |
| **읽을 문서 ≠ 링크 대상** | 합치면 이미지 임베드 582건을 깨진 링크로 오보한다 |
| lint 제외는 **커밋되는 설정 파일**에 | 무엇을 왜 뺐는지가 감사 대상 |
| `main` 은 정수를 돌려주고 `sys.exit` 은 파일 끝 한 줄에만 | 프로세스 없이 테스트한다 |
| **바뀔 것을 이음매 하나에 가둔다** | `doc_iri`(정체성) · `resolve` 인자(해석) |
| 「있는가」가 아니라 **「결과가 달라지는가」** 를 잰다 | 펜스 혼용 10건, 파싱 차이 0 |

### 실측해둔 숫자 (2026-08-24)

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
| `links_to` | 10,622 | 9,359 | 집합이라 중복 1,162 이 접힌다 |
| `part_of` | 1,020 | 4,758 | 폴더가 리소스가 됐다 |
| **합계** | 엣지 12,057 | **트리플 27,515** | |

빌드 SQLite 1.3s · RDF 1.7s. 노트 4,204 · lint 382.

> **`800 TRPG` 가 2026-08-23 에 vault 밖으로 나갔다** — [`800-trpg-split.md`](800-trpg-split.md).
> Phase 6·9 의 실습 대상이 「제외 구역」에서 **「출처가 다른 독립 코퍼스」** 로 바뀌었고,
> 문제가 약해진 게 아니라 **RDF 가 원래 풀려던 문제**가 됐다.

---

## 바로 다음 — Phase 7 Step 1 `SELECT`·`WHERE`·`FILTER` (RED)

### 왜 이게 중요한가

**Phase 5 에서 SQL 로 푼 질문을 하나씩 다시 푼다.** 답이 같아야 하고 표현이 달라야 한다.

> 결과가 SQLite 와 **일치**한다 (다르면 Phase 6 모델링이 틀린 것)

완료 기준의 이 줄이 핵심이다. **SPARQL 이 다른 답을 내면 질의가 아니라 모델을 의심한다.**

### 이 Phase 의 산출물은 코드가 아니라 비교표다

```
| 질의 | SQL | SPARQL | 판정 |
```

가이드가 예상을 적어뒀다 — 이행 폐쇄와 역방향 순회는 SPARQL 압승, 문자열 가공은
SQL 우세, **성능은 물음표.** 그 물음표를 재는 게 Phase 7 의 일이다.

**SPARQL 홍보가 아니다.** 어디서 갈리는지 재는 것이다.

### 할 일

새 파일 `vault/sparql.py` 와 `tests/test_sparql.py`.
`q type` · `q tag` 를 SPARQL 로 재현하고 **SQLite 결과와 대조**한다.

SQL 은 「테이블에서 행을 고른다」, SPARQL 은 **「그래프에서 모양을 찾는다」**.
트리플 패턴을 나열하면 공통 변수로 자동 조인되고 `JOIN ... ON` 이 없다.

`uv run pytest -v` → 기존 199개 통과, 새 테스트가 `ModuleNotFoundError`.

---

## 그 다음 — Phase 7 Step 2~6

| Step | 내용 | 핵심 |
|---|---|---|
| 2 | `OPTIONAL` | summary 없는 문서도 나오게 |
| 3 | **property path `+`** | 재귀 CTE 여섯 줄이 한 글자가 된다. **결과 대조** |
| 4 | **`^` 역방향** | `q near` 의 `UNION ALL` 이 `\|^` 한 줄 |
| 5 | 집계 | `q stats` |
| 6 | **비교표** | 코드 길이 · 실행 시간 · 읽기 쉬움 |

Step 3 에서 **깊이를 잃는다.** `+` 는 몇 단 위인지 안 알려준다.
Phase 5 의 `learning_path` 가 돌려주던 그 숫자를 SPARQL 로 어떻게 낼지가 실제 과제다.

완료 기준은 [`phase07.md`](phase07.md) 참조.

---

## 커밋 규칙 (Conventional Commits)

**기본은 하나로 담는다.** 구현 · 테스트 · `learnings/` · 문서 갱신까지 커밋 하나.
Step 하나가 곧 커밋 하나다. 잘게 쪼개면 이력이 오히려 안 읽힌다.

| 시점 | type | 예 |
|---|---|---|
| GREEN (구현·테스트·학습노트 함께) | `feat` | `feat(frontmatter): fm_list — 리스트 블록 파싱` |
| 실측 (스크립트·결과·회고 함께) | `feat(tools)` | `feat(tools): Phase 1 파서 실측` |
| REFACTOR | `refactor` | `refactor(frontmatter): 키 매칭 정규식을 헬퍼로 추출` |
| 기존 동작이 틀렸던 것 | `fix` | `fix(links): 표 안의 \| 가 타깃 끝에 역슬래시를 남기던 문제` |
| **코드가 안 바뀐 때만** | `docs` | `docs: Phase 2 가이드 — 위키링크 파서` |

- RED는 커밋하지 않는다 — 실패 상태가 이력에 남으면 `git bisect`를 못 쓴다. GREEN 커밋에 테스트가 같이 들어가므로 명세는 보존된다
- GREEN과 REFACTOR를 **한 커밋에 섞지 않는다.** 섞으면 diff에서 "기능이 바뀐 건가 정리한 건가"를 읽을 수 없다
- 메시지는 **영어로, 제목 한 줄 + 불릿 2~3개.** 길게 쓰지 않는다. 함정과 설계 결정의 상세는 `learnings/`가 맡는다
- `Co-Authored-By` 트레일러는 쓰지 않는다
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

---

## 진행 방식 요약

```
RED       테스트를 쓴다 → 실패를 눈으로 확인
GREEN     최소 구현 → 통과 → 커밋
REFACTOR  개선점 검토 (없으면 "없다"고 판단하는 것도 결과) → 있으면 별도 커밋
실측       실제 vault에 돌려 답안지 출력과 대조
```

**단위 테스트가 전부 초록이어도 실제 데이터에서 숫자가 다르면 틀린 것이다.**
