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

**Phase 2 (위키링크 파서) · Step 1 — RED 작성 직전**

Phase 1 완료. 테스트 16개 통과.

| Phase 1 | 상태 |
|---|---|
| Step 1 `split_frontmatter` | ✅ GREEN · REFACTOR 판단 완료(안 고침) |
| Step 2 `fm_get` | ✅ GREEN · REFACTOR 판단 완료(안 고침) |
| Step 3 `fm_list` | ✅ GREEN · REFACTOR 판단 완료(안 고침) |
| Step 4 실측 | ✅ `tools/measure_phase01.py` |
| 회고 | ✅ `learnings/phase01-measure-then-decide.md` |

| Phase 2 | 상태 |
|---|---|
| **Step 1 `link_target`** | **⬜ 여기부터** |
| Step 2 `strip_code` | ⬜ |
| Step 3 `iter_links` | ⬜ |
| Step 4 실측 | ⬜ |

`vault/frontmatter.py`에 함수 셋이 있다. Phase 2는 **새 모듈** `vault/links.py`다.

### 여기까지 오면서 확정한 것

| 결정 | 근거 |
|---|---|
| Phase 1~5는 표준 라이브러리만 | 파서를 손으로 짜는 게 학습의 핵심. Phase 6에서 `rdflib` 들어오며 의도적으로 해제 |
| `split_frontmatter`는 `re.match` | 앵커링을 정규식(`^`)이 아니라 호출 방식으로 강제 |
| 빈 값·부재는 `fm_get` → `None` | 호출부가 둘을 구분할 이유가 없다 |
| 빈 값·부재는 `fm_list` → `[]` | 리스트는 "비어 있음 = 없음". 분기가 사라진다 |
| 인라인 리스트 `key: [a, b]` 미지원 | vault가 안 쓴다. 콜론 뒤 `\n`을 요구해 패턴으로 배제 |
| 빈 frontmatter·CRLF·블록 안 빈 줄 대응 안 함 | 실측 전부 0건. 없는 입력에 대비한 코드는 검증할 수 없어 썩는다 |
| `tools/`에는 테스트를 안 붙인다 | 일회성 계측. 대신 **출력을 눈으로 검산**하는 게 유일한 방어선 |
| 실측은 제외 전·후를 둘 다 낸다 | 답안지 숫자가 `GRAPH_EXCLUDE` 적용 후 값이라 그냥 비교하면 안 맞는다 |

### 실측해둔 숫자 (2026-08-18)

`uv run python -m tools.measure_phase01`

| 항목 | 전체 | 제외 후 | 답안지(08-11) |
|---|---:|---:|---:|
| md 파일 | 6,462 | 3,984 | 6,289 |
| frontmatter | 5,837 (90.3%) | 3,974 (99.7%) | |
| `type` | 5,796 | 3,974 | |
| `summary` | 1,126 | 1,126 | |
| `builds_on` 항목 | 393 | 393 | 387 |
| `supersedes` 항목 | 3 | 3 | 3 |

```
summary 길이   min 2 · median 60 · p95 76 · max 80 · 초과 0
type 13값 밖   제외 후 0건
빈 frontmatter · CRLF · 블록 안 빈 줄   전부 0
```

제외 구역 밖에 `type`을 가진 문서가 1,822개 있다 (`완제품` 1,042 · `원재료` 351 ·
`중간재` 316 · `마물` 101 · `마족` 12). **`800 TRPG`는 같은 키를 게임 아이템
분류로 쓴다.** 안 빼면 문서 유형 분포 1위가 `완제품`이 된다.

프로젝트 시작 시점(2026-08-10)은 6,289개 / frontmatter 37.7%였다.
**마이그레이션이 먹혔고 vault는 계속 자란다.**

---

## 바로 다음 — Phase 2 Step 1 `link_target` (RED)

### 왜 이게 중요한가

Phase 1이 명시적 관계 396개(`builds_on` 393 + `supersedes` 3)를 읽었다면,
Phase 2는 **나머지 전부**를 읽는다. 답안지 기준 `links_to` 10,702개로 전체
엣지 12,266개의 대부분이다.

이쪽 함정은 **크래시를 내지 않는다.** 조용히 숫자를 틀리게 만든다.
스키마 정본에 실제 사고가 적혀 있다.

> 표 안의 이스케이프된 파이프 `\|`를 반드시 처리해야 한다. 안 하면 표로 정리된
> 인덱스 문서의 링크를 전부 깨진 것으로 세고, **반대로 그 링크가 가리키는
> 문서를 고아로 오판한다** (500 Mind Compiler를 45.7% 고아로 오측정한 원인).

파싱 실수 하나가 두 통계를 **반대 방향으로** 망가뜨렸다.

### 할 일

새 파일 `vault/links.py`와 `tests/test_links.py`를 만든다.
`link_target(raw)`은 `[[ ]]` **안쪽 문자열**을 받아 링크 대상 이름을 돌려준다.

자를 구분자와 **순서**가 핵심이다.

```
\|  →  |  →  #  →  ^
```

`|`를 먼저 자르면 `\|`의 역슬래시가 타깃 끝에 남는다. 답안지 함정 표의 1번이다.

테스트로 고정할 입력.

| 입력 | 기대 |
|---|---|
| `문서` | `문서` |
| `문서\|별칭` | `문서` |
| `문서\\|별칭` (표 안) | `문서` — 역슬래시가 남으면 안 된다 |
| `문서#헤딩` | `문서` |
| `문서#헤딩\|별칭` | `문서` |
| `문서^blockid` | `문서` |
| `폴더/문서` | `폴더/문서` — 경로는 남긴다 |
| `  문서  ` | `문서` |

`uv run pytest -v` → 기존 16개 통과, 새 테스트가 `ImportError`.
**실패를 눈으로 본 뒤** GREEN으로 간다.

---

## 그 다음 — Phase 2 Step 2~4

| Step | 함수 | 핵심 함정 |
|---|---|---|
| 2 | `strip_code` | 펜스(``` / ~~~) 짝 맞추기 · 인라인 코드 · **줄 번호 보존**(삭제가 아니라 빈 줄로 치환) |
| 3 | `iter_links` | 이스케이프 `\[[` · 임베드 `![[` · 대괄호 중첩 |
| 4 | 실측 | vault 전체 링크 수 → 답안지 24,969와 대조 |

Step 3에서 **본문만 본다.** `split_frontmatter`가 준 본문을 쓴다.
frontmatter의 `builds_on`을 링크로 또 세면 같은 관계가 두 번 들어간다.

Phase 2 완료 기준은 [`phase02.md`](phase02.md) 참조.

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
- 본문에는 **밟은 함정과 설계 결정**을 남긴다. 3개월 뒤 `git log`가 학습 노트가 된다
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
