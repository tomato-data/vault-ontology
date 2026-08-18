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

**Phase 4 (검증은 거부다) · Step 1 — RED 작성 직전**

Phase 1~3 완료. 테스트 66개 통과.

| Phase | 내용 | 상태 |
|---|---|---|
| 1 | `split_frontmatter` · `fm_get` · `fm_list` · 실측 | ✅ |
| 2 | `link_target` · `strip_code` · `iter_links` · 실측 | ✅ |
| 3 | `scan_vault` · `resolve_link` · 충돌 감지 · 실측 · `source` | ✅ |
| **4** | **1 `vault/schema.py` — 상수와 `validate()`** | **⬜ 여기부터** |
| 4 | 2 태그 검출기 · 3 제외 규칙 · 4 CLI · 5 실측 | ⬜ |
| 5~9 | | ⬜ |

`vault/` 에 `frontmatter.py` · `links.py` · `scan.py` 가 있다.
Phase 4는 **새 모듈 둘** — `schema.py` · `lint.py`, 그리고 `__main__.py`.

### 이 프로젝트가 무엇인가

이건 파서 재구현 연습이 아니라 **내 vault 를 강화하는 작업**이다. 기존 `vault-cli`
와 스키마 정본은 Claude 가 만들었고, 동작하지만 **내 의도와 어긋난 자리가 남아
있다.** 그걸 찾아 메우는 게 실질이다.

`reference/` 와 스키마 정본은 **권위가 아니라 검토 대상**이다.
"정본에 그렇게 적혀 있다" 는 논증의 끝이 아니라 시작이다.

실제 산출물 (Phase 2~3):

- 정본 v1.8 — `builds_on` 선택 기준 신설 (통과 조건 3 · 고르는 규칙 3 · 금지 4)
- CLAUDE.md v2.43 — 태그 규칙 완화 (기존 어휘 안에서만 Claude 가 단다 · 붙이면 보고)
- vault 문서 수정 3건 — `[[Docker.md]]` · `WORKLOG.md` 2건 개명

### 여기까지 오면서 확정한 것

| 결정 | 근거 |
|---|---|
| Phase 1~5는 표준 라이브러리만 | Phase 6에서 `rdflib` 들어오며 의도적으로 해제 |
| `split_frontmatter`는 `re.match` | 앵커링을 정규식이 아니라 호출 방식으로 강제 |
| 부재는 `fm_get` → `None`, `fm_list` → `[]` | 리스트는 "비어 있음 = 없음" |
| `link_target`은 `fm_list` **밖**에서 | `fm_list`는 `tags:`도 읽는다. `Stack/C#`이 잘린다 |
| `strip_code`는 줄을 비운다 (안 지운다) | 호출부가 `file:line`으로 보고한다 |
| `iter_links`는 본문만 받는다 | frontmatter의 `builds_on`을 또 세면 관계가 두 번 |
| 정규화는 **경계에서 한 번만** | `scan_vault`가 파일명을, `resolve_link`가 타깃을 |
| 동명이인은 **이름이 아니라 해석기**를 고친다 | 경로가 이미 아는 걸 파일명에 또 넣지 않는다 |
| 「가깝다」 = **소스와 같은 폴더** | 형제 폴더는 안 친다. 넓히면 1,443개가 틀린 곳으로 |
| `tools/`에는 테스트를 안 붙인다 | 대신 **출력을 눈으로 검산**한다 |
| 「있는가」가 아니라 **「결과가 달라지는가」** 를 잰다 | 펜스 혼용 10건 있으나 파싱 차이 0 |

### 안 고치기로 한 것 (전부 실측 후)

| 입력 | 실측 |
|---|---|
| 빈 frontmatter · CRLF · 리스트 블록 안 빈 줄 | 0건 |
| 이름에 `#`·`^`가 든 문서 | 0건 |
| ` ``` `와 `~~~` 혼용 | 10파일, **파싱 차이 0** |
| 이중 백틱 인라인 | 13건 |
| `[[Docker.md]]` 처럼 확장자 붙은 타깃 | 1건. **받아주면 lint가 잡을 걸 파서가 먹는다** |
| 대소문자 충돌 3무리 | 서로 다른 문서. 어느 쪽이 옳다고 할 근거가 없다 |
| `supersedes` 가 죽은 문서를 가리킴 | **정상.** 과거를 가리키는 관계다 |

전체 목록은 [`learnings/phase01-qa.md`](../learnings/phase01-qa.md) ·
[`phase02-qa.md`](../learnings/phase02-qa.md) ·
[`phase03-qa.md`](../learnings/phase03-qa.md).
정규식 조각 사전은 [`regex-reference.md`](../learnings/regex-reference.md).

### 실측해둔 숫자 (2026-08-18)

```
uv run python -m tools.measure_phase01
uv run python -m tools.measure_phase02
uv run python -m tools.measure_phase03
```

| 항목 | 전체 | 제외 후 | 답안지 |
|---|---:|---:|---:|
| md 파일 | 6,462 | 3,985 | 6,289 |
| `scan_vault` (점 디렉토리 제외) | 6,435 | | |
| frontmatter | 5,837 (90.3%) | 3,974 (99.7%) | |
| `builds_on` / `supersedes` 항목 | 393 / 3 | | 387 / 3 |
| 본문 링크 | 24,371 | 10,735 | 24,969 |
| 미해결 | 1,977 (8.1%) | 1,445 | 2,343 (9.4%) / 1,694 |
| 동명이인 | 66 이름 (244 파일) | | |
| 대소문자 충돌 | 3 무리 | | |
| NFD 로 저장된 파일 | 1,091 | | |

**정규화가 살린 링크 5,341개(21.9%).** 안 했으면 한국어 링크가 대량으로 깨진 것으로
잡혔다. `source` 를 넘겨 제자리를 찾은 링크 126개.

---

## 바로 다음 — Phase 4 Step 1 `vault/schema.py` (RED)

### 왜 이게 중요한가

Phase 1~3은 **읽는 쪽**이었다. 여기는 **판정하는 쪽**이다. 그리고 Phase 1~3의 함수를
처음으로 **전부 한자리에 모아** 쓴다 — 여기서 코드가 도구가 된다.

핵심 원칙이 둘이다.

**1. 경고는 무시된다.** 정본이 근거를 실측으로 적어뒀다 — `summary` 80자를 프롬프트로
부탁했더니 14% 가 위반했고, hex 태그는 청소해도 다시 쌓였다.
**규칙은 배출구를 못 이긴다.** 그래서 위반은 전부 **거부**다.

**2. 생성과 검사가 같은 함수를 쓴다.**

```
vault new   → 검증 통과한 문서만 생성
vault lint  → 검증 실패한 문서 검출
                  ↑ 같은 validate()
```

따로 만들면 반드시 어긋난다. `vault new` 는 이 로드맵 범위 밖이지만 `validate()` 를
그 전제로 설계한다.

### 할 일

새 파일 `vault/schema.py` 와 `tests/test_schema.py`.

```
TYPES = { ... 13값 }
SUMMARY_MAX = 80
BUILDS_ON_MAX = 3
validate(fm, ...) -> [위반 목록]
```

검사할 제약은 [`phase04.md`](phase04.md) 의 표. `builds_on` 대상 검사는 Phase 3의
`resolve_link` 를 쓴다 — **여기서 모듈이 처음 서로를 부른다.**

반환 형태를 먼저 정한다. 예외를 던지지 않고 **위반 목록을 돌려준다.** 문서 하나에
위반이 여럿일 수 있고, lint 는 전부 보고해야 한다.

`uv run pytest -v` → 기존 66개 통과, 새 테스트가 `ModuleNotFoundError`.

---

## 그 다음 — Phase 4 Step 2~5

| Step | 내용 | 핵심 |
|---|---|---|
| 2 | 의도치 않은 태그 검출기 | **오탐 4종**을 피하는 게 어렵다 |
| 3 | `.vault-lint.json` 제외 규칙 | 코드에 하드코딩하지 않는다. **커밋한다** |
| 4 | CLI (`__main__.py`) | argparse · 보고 형식 · **종료 코드 0/1/2** |
| 5 | 실측 | 답안지 `lint` 출력과 위반 건수 대조 |

Step 2 의 오탐 4종. 하나씩 잘못 잡고 고친 이력이 있다.

```
[EC2](#ec2-elastic-…)   마크다운 링크 목적지
https://…#_oidc         URL 조각
#Stack/Python           사람이 다는 계층 태그
#729651                 순수 숫자 — Obsidian은 태그로 안 만든다
```

**"무엇을 잡을까"보다 "무엇을 잡으면 안 되나"가 어렵다.** 오탐 하나가 유저 문서를
망가뜨린다 — 실제로 `#729651`(포럼 글번호)을 이스케이프해 본문을 오염시킨 사고가 있었다.

Phase 4 완료 기준은 [`phase04.md`](phase04.md) 참조.

vault 쪽 백로그(어떤 개선을 어느 Phase 에서 처리할지)는
[`vault-backlog.md`](vault-backlog.md). **Phase 4 에서 처리할 항목이 넷 있다.**

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
