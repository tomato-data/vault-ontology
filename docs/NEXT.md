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

**Phase 3 (vault 스캔 · 링크 해석) · Step 1 — RED 작성 직전**

Phase 1~2 완료. 테스트 42개 통과.

| Phase | Step | 상태 |
|---|---|---|
| 1 | `split_frontmatter` · `fm_get` · `fm_list` · 실측 | ✅ |
| 2 | `link_target` · `strip_code` · `iter_links` · 실측 | ✅ |
| **3** | **1 `scan_vault`** | **⬜ 여기부터** |
| 3 | 2 `resolve_link` · 3 충돌 감지 · 4 실측 | ⬜ |
| 4~9 | | ⬜ |

`vault/frontmatter.py` · `vault/links.py` 에 함수 여섯이 있다.
Phase 3은 **새 모듈** `vault/scan.py` 다.

### 이 프로젝트가 무엇인가

Phase 2 에서 분명해진 것. 이건 파서 재구현 연습이 아니라 **내 vault 를 강화하는
작업**이다. 기존 `vault-cli` 와 스키마 정본은 Claude 가 만들었고, 동작하지만
**내 의도와 어긋난 자리가 남아 있다.** 그걸 찾아 메우는 게 실질이다.

그러므로 `reference/` 와 스키마 정본은 **권위가 아니라 검토 대상**이다.
"정본에 그렇게 적혀 있다" 는 논증의 끝이 아니라 시작이다.

실제로 Phase 2 에서 `builds_on` 선택 기준이 비어 있는 걸 찾아 정본 v1.8 을 냈다.
**산출물은 코드만이 아니다. vault 자체의 개선이 같은 비중이다.**

### 여기까지 오면서 확정한 것

| 결정 | 근거 |
|---|---|
| Phase 1~5는 표준 라이브러리만 | 파서를 손으로 짜는 게 학습의 핵심. Phase 6에서 `rdflib` 들어오며 의도적으로 해제 |
| `split_frontmatter`는 `re.match` | 앵커링을 정규식(`^`)이 아니라 호출 방식으로 강제 |
| 빈 값·부재는 `fm_get` → `None`, `fm_list` → `[]` | 리스트는 "비어 있음 = 없음". 호출부의 분기가 사라진다 |
| 인라인 리스트 `key: [a, b]` 미지원 | vault가 안 쓴다. 콜론 뒤 `\n`을 요구해 패턴으로 배제 |
| `link_target`은 `fm_list` **밖**에서 적용 | `fm_list`는 `tags:`도 읽는다. 태그에 씌우면 `Stack/C#`이 잘린다 |
| `strip_code`는 줄을 지우지 않고 비운다 | 호출부가 `file:line`으로 보고한다 |
| `iter_links`는 본문만 받는다 | frontmatter의 `builds_on`을 또 세면 관계가 두 번 들어간다 |
| `tools/`에는 테스트를 안 붙인다 | 일회성 계측. **출력을 눈으로 검산**하는 게 유일한 방어선 |
| 실측은 제외 전·후를 둘 다 낸다 | 답안지 숫자가 `GRAPH_EXCLUDE` 적용 후 값이다 |
| 「있는가」가 아니라 「결과가 달라지는가」를 잰다 | 펜스 혼용 10건이 있었으나 파싱 차이 0건이었다 |

### 안 고치기로 한 것 (전부 실측 후 판단)

| 입력 | 실측 |
|---|---|
| 빈 frontmatter · CRLF · 리스트 블록 안 빈 줄 | 0건 |
| 이름에 `#`·`^`가 든 문서 | 0건 |
| ` ``` `와 `~~~` 혼용 | 10파일 있으나 **파싱 결과 차이 0** |
| 이중 백틱 인라인 | 13건. 영향 미미 |

깨지는 지점 전체 목록은 [`learnings/phase01-qa.md`](../learnings/phase01-qa.md) ·
[`phase02-qa.md`](../learnings/phase02-qa.md).
정규식 조각 사전은 [`learnings/regex-reference.md`](../learnings/regex-reference.md).

### 실측해둔 숫자 (2026-08-18)

```
uv run python -m tools.measure_phase01
uv run python -m tools.measure_phase02
```

| 항목 | 전체 | 제외 후 | 답안지(08-11) |
|---|---:|---:|---:|
| md 파일 | 6,462 | 3,985 | 6,289 |
| frontmatter | 5,837 (90.3%) | 3,974 (99.7%) | |
| `type` | 5,796 | 3,974 | |
| `builds_on` 항목 | 393 | 393 | 387 |
| `supersedes` 항목 | 3 | 3 | 3 |
| 링크 | 24,423 | **10,731** | `links_to` **10,702** |

`summary` 길이 `min 2 · median 60 · p95 76 · max 80 · 초과 0`.
`type` 13값 밖은 제외 후 0건 (제외 전에는 `800 TRPG`의 5값 1,822건).

**두 함정이 막아낸 오차 357개** — 표 안의 `\|` 101개(`500 Mind Compiler`에 몰림),
코드 예제 속 가짜 엣지 256개(스킬 정의·템플릿·가이드라인 문서).

---

## 바로 다음 — Phase 3 Step 1 `scan_vault` (RED)

### 왜 이게 중요한가

Phase 2까지는 **문서 하나**를 읽었다. `iter_links`가 뱉는 `CIDR`은 아직 문자열일
뿐 아무것도 가리키지 않는다. 여기서 그 문자열이 파일이 된다.

표면은 파일 탐색인데 실제로 푸는 문제는 이것이다.

> **이름은 식별자가 아니다.**

**Phase 6의 IRI 설계가 이 경험을 재료로 쓴다.** RDF는 모든 것에 전역 식별자를
요구하고, "경로로 할까 이름으로 할까 새 ID를 줄까"가 그때의 첫 결정이다.

### Step 1의 함정 둘

**NFC / NFD.** macOS 파일시스템은 파일명을 **NFD**(자모 분리)로 저장한다.
본문에 타이핑한 `[[한글]]`은 **NFC**다. 눈으로는 같은데 문자열 비교가 실패한다.
**한국어 vault라 이걸 안 맞추면 링크가 대량으로 깨진 것으로 잡힌다.**
양쪽 다 `unicodedata.normalize("NFC", s)`를 통과시킨다.

**`os.path.splitext` 금지.**

```
splitext("No.013 현자의 돌")  →  ("No", ".013 현자의 돌")
```

확장자가 없는 이름을 쪼갠다. `removesuffix(".md")`로 `.md`만 명시적으로 뗀다.

### 할 일

새 파일 `vault/scan.py`와 `tests/test_scan.py`. `scan_vault(root)`는 파일 목록과
이름 인덱스를 돌려준다. 제외할 디렉토리(`.git` · `.obsidian` · `.trash`)도 여기서
정한다.

`uv run pytest -v` → 기존 42개 통과, 새 테스트가 `ImportError`.

---

## 그 다음 — Phase 3 Step 2~4

| Step | 내용 | 핵심 |
|---|---|---|
| 2 | `resolve_link` | 이름 → 경로 포함 → 꼬리 매칭 → 미해결 |
| 3 | 충돌 감지 | 대소문자 무시 충돌 · 동명이인(`Hub.md`가 여럿) |
| 4 | 실측 | 깨진 링크 수 · 고아 노트 수 |

미해결이 곧 오류는 아니다. **자리표시자 · 외부 참조 · 진짜 유실** 셋으로 갈리고
처리가 다르다. 완료 기준은 [`phase03.md`](phase03.md) 참조.

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
