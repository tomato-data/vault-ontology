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

**Phase 5 (SQLite 그래프) · Step 1 — RED 작성 직전. 1부의 마지막이다.**

Phase 1~4 완료. 테스트 110개 통과.

| Phase | 내용 | 상태 |
|---|---|---|
| 1 | `split_frontmatter` · `fm_get` · `fm_list` | ✅ |
| 2 | `link_target` · `strip_code` · `iter_links` | ✅ |
| 3 | `scan_vault` · `resolve_link` · 충돌 감지 · `source` | ✅ |
| 4 | `schema.py` · 태그 검출기 · 제외 규칙 · CLI | ✅ |
| **5** | **1 스키마 + `build`** | **⬜ 여기부터** |
| 5 | 2 `part_of` · 3 단순 질의 · 4 재귀 CTE · 5 이웃·고아 · 6 답안지 대조 | ⬜ |
| 6~9 | 온톨로지 (2부) | ⬜ |

`vault/` 에 `frontmatter.py` · `links.py` · `scan.py` · `schema.py` · `lint.py` ·
`__main__.py` 가 있다. Phase 5는 **새 모듈** `graph.py`.

### 이 프로젝트가 무엇인가

파서 재구현 연습이 아니라 **내 vault 를 강화하는 작업**이다. 기존 `vault-cli` 와
스키마 정본은 Claude 가 만들었고, 동작하지만 **내 의도와 어긋난 자리가 남아 있다.**

`reference/` 와 정본은 **권위가 아니라 검토 대상**이다.
"정본에 그렇게 적혀 있다" 는 논증의 끝이 아니라 시작이다.

Phase 4 에서 그 간극이 처음 **코드의 우위**로 나타났다 — 우리 lint 가 답안지가
구조적으로 못 보는 24건을 찾았고, 그중 23건이 정본이 요구하는데 구현이 없던 검사다.

**작동 방식: 실제로 쓰면서 부족한 걸 고쳐 나간다.**

실제 산출물 (Phase 2~4):

- 정본 v1.8 — `builds_on` 선택 기준 신설
- CLAUDE.md v2.43 — 태그 규칙 완화 (기존 어휘 안에서만 · 붙이면 보고)
- 죽은 태그 어휘 13종 삭제 · 충돌 사본 8건 정리 · `.vault-lint.json` 재설계
- **끊겨 있던 pre-commit 훅 복구** — 홈 디렉토리 개명으로 경로가 깨져, 모든 커밋을
  막으면서 유실 검사는 하나도 못 하고 있었다

### 여기까지 오면서 확정한 것

| 결정 | 근거 |
|---|---|
| Phase 1~5는 표준 라이브러리만 | Phase 6에서 `rdflib` 들어오며 해제 |
| 부재는 `fm_get` → `None`, `fm_list` → `[]` | 리스트는 "비어 있음 = 없음" |
| `link_target`은 `fm_list` **밖**에서 | `fm_list`는 `tags:`도 읽는다 |
| `strip_code`는 줄을 비운다 (안 지운다) | 호출부가 `file:line`으로 보고한다 |
| 정규화는 **경계에서 한 번만** | 링크 5,341개(21.9%)가 여기 걸려 있다 |
| 동명이인은 **이름이 아니라 해석기**를 고친다 | 경로가 아는 걸 파일명에 또 넣지 않는다 |
| 「가깝다」 = **소스와 같은 폴더** | 넓히면 1,443개가 틀린 곳으로 간다 |
| **읽을 문서 ≠ 링크 대상** | 합치면 이미지 임베드 582건을 깨진 링크로 오보한다 |
| `validate`는 예외 대신 **목록**을 돌려준다 | 문서 하나가 여러 규칙을 어긴다 |
| lint 제외는 **코드가 아니라 커밋되는 설정 파일**에 | 무엇을 왜 뺐는지가 감사 대상 |
| 기본값은 **비운다** | 설정이 없으면 전부 검사한다. 안전한 방향 |
| `main` 은 정수를 돌려주고 `sys.exit` 은 파일 끝 한 줄에만 | 프로세스 없이 테스트한다 |
| 「있는가」가 아니라 **「결과가 달라지는가」** 를 잰다 | 펜스 혼용 10건, 파싱 차이 0 |

### 반복해서 나온 함정 — 경계

문자열 접두사는 경계를 모른다. **다섯 번** 나왔다.

```
Phase 2   \|  vs  |            긴 것부터 자른다
Phase 3   Net|work             꼬리 매칭에 슬래시를 붙인다
Phase 3   302.6 vs 302.60      컴포넌트 단위로 센다
Phase 4   800 TRPG vs 800 TRPG Archive
Phase 4   #  앞이 공백일 것      오탐 6종이 한 번에 사라진다
```

정규식 조각 사전은 [`learnings/regex-reference.md`](../learnings/regex-reference.md).

### 실측해둔 숫자

```
uv run python -m tools.measure_phase01     # 02, 03 도 있다
uv run python -m vault lint
```

| 항목 | 값 | 답안지 |
|---|---:|---:|
| 노트 (점 디렉토리 제외) | 6,430 | |
| 링크 대상 (첨부 포함) | 7,353 | |
| 본문 링크 | 24,371 | 24,463 |
| `builds_on` / `supersedes` | 393 / 3 | 387 / 3 |
| 동명이인 | 66 이름 · 244 파일 | |
| NFD 로 저장된 파일 | 1,091 | |
| **lint 위반** | **354** | |
| ↳ 깨진 링크 | 328 | 267 |
| ↳ frontmatter | 26 | **2** |

---

## 바로 다음 — Phase 5 Step 1 스키마와 `build` (RED)

### 왜 이게 중요한가

지금까지 읽고 판정했다. 이제 **저장하고 질의한다.** Phase 1~4의 모든 함수가 여기
들어오고, **1부의 종착점이자 2부의 대조본**이 된다.

### 핵심 개념 셋

**1. 그래프는 파생물이다.** md 가 원본이고 DB 는 언제든 다시 만든다. 그래서 MERGE ·
제약조건 · 멱등성이 필요 없다. **매번 지우고 새로 만든다.** `.vault-graph.db` 는
gitignore. 이 성질이 2부의 RDF 그래프에도 그대로 간다.

**2. `dst` 가 NULL 을 허용하고 `raw` 를 같이 저장한다.**

```sql
CREATE TABLE edge (
  src  TEXT NOT NULL,
  dst  TEXT,               -- 해석 실패면 NULL
  raw  TEXT NOT NULL,      -- 원래 쓰인 타깃 문자열
  kind TEXT NOT NULL
);
```

**깨진 링크도 그래프의 사실이다.** 버리면 "무엇을 가리키려 했는가" 를 잃는다.
lint 가 세는 328건이 여기 들어간다.

**3. 파생 가능한 사실은 저장하지 않는다.** `part_of`(디렉토리 계층)는 frontmatter 에
안 쓰고 빌드 시점에 경로에서 유도한다(Step 2). `updated` 가 없는 것도 같은 이유 —
git 이 안다.

### 할 일

새 파일 `vault/graph.py` 와 `tests/test_graph.py`. 세 테이블(`node` · `edge` · `tag`)을
만들고 vault 를 적재한다. `sqlite3` 는 표준 라이브러리다.

제외 구역은 `800 TRPG` · `900 Archive` · 점 디렉토리 · `CLAUDE.md`.
**빼도 링크는 그쪽을 가리키므로**, 해석 실패를 두 줄로 나눠 보고한다 —
제외 구역을 가리키는 것(정상)과 그 밖(진짜 깨짐).

`uv run pytest -v` → 기존 110개 통과, 새 테스트가 `ModuleNotFoundError`.

---

## 그 다음 — Phase 5 Step 2~6

| Step | 내용 | 핵심 |
|---|---|---|
| 2 | `part_of` 유도 | 경로에서 만든다. 저장하지 않는다 |
| 3 | `q stats` · `q type` · `q tag` | 단순 질의 |
| 4 | **`q path` — 재귀 CTE** | 이 여섯 줄을 손으로 써봐야 Phase 7의 한 줄이 값을 한다 |
| 5 | `q near` · `q orphans` | 이웃과 고아 |
| 6 | **답안지 대조** | 같은 날 둘 다 돌려 노드·엣지·태그 수가 **전부 일치**해야 한다 |

Step 4 의 `UNION`(`UNION ALL` 이 아니라)이 중복을 제거해 **순환에서 무한루프를 막는다.**
`depth < 10` 은 이중 안전장치.

Step 6 이 1부 전체의 판정이다. 하나라도 다르면 **어느 Phase 에서 갈렸는지 역추적한다.**

완료 기준에 **「1부 회고」** 가 따로 있다 — 손으로 짜본 것과 읽기만 한 것의 차이.

vault 쪽 백로그는 [`vault-backlog.md`](vault-backlog.md).
**Phase 5 직후에 태그 어휘를 그래프로 재보기로 했다.**

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
