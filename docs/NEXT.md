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

### 답안지에 대하여

답안지는 `~/Desktop/Code/vault-cli`다. **막히기 전에는 열지 않는다.**

> ⚠️ **vault-cli는 원격 저장소가 없다.** 이 Mac에만 있다.
> Phase 1~4는 답안지 없이도 진행할 수 있지만, **Phase 5의 대조 단계에서는 `vault.py`를 직접 돌려야 한다.**
> 그 전에 vault-cli를 GitHub(private로 충분)에 올리거나, 다른 방법으로 양쪽 Mac에 두어야 한다.

vault 경로는 두 Mac 모두 같다.

```
~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault
```

---

## 현재 위치

**Phase 1 (frontmatter 파서) · Step 3 — RED 작성 직전**

| | 상태 |
|---|---|
| Step 1 `split_frontmatter` | ✅ GREEN · REFACTOR 판단 완료(안 고침) |
| Step 2 `fm_get` | ✅ GREEN · REFACTOR 판단 완료(안 고침) |
| **Step 3 `fm_list`** | **⬜ 여기부터** |
| Step 4 실측 | ⬜ |

테스트 10개 통과 상태. `vault/frontmatter.py`에 `split_frontmatter`, `fm_get` 두 함수가 있다.

### 여기까지 오면서 확정한 것

| 결정 | 근거 |
|---|---|
| Phase 1~5는 표준 라이브러리만 | 파서를 손으로 짜는 게 학습의 핵심. Phase 6에서 `rdflib` 들어오며 의도적으로 해제 |
| `split_frontmatter`는 `re.match` | 앵커링을 정규식(`^`)이 아니라 호출 방식으로 강제 |
| 빈 값·부재는 `fm_get` → `None` | 호출부가 둘을 구분할 이유가 없다 |
| 빈 값·부재는 `fm_list` → `[]` | 리스트는 "비어 있음 = 없음". 분기가 사라진다 |
| 빈 frontmatter·CRLF 대응 안 함 | 실측 0건. 없는 입력에 대비한 코드는 검증할 수 없어 썩는다 |

### 실측해둔 숫자 (2026-08-16)

```
md 파일          6,452
--- 로 시작       5,835  (90.4%)
빈 frontmatter   0
CRLF 포함        0
```

프로젝트 시작 시점(2026-08-10)은 6,289개 / frontmatter 37.7%였다. **마이그레이션이 먹혔고 vault는 계속 자란다.**

---

## 바로 다음 — Step 3 `fm_list` (RED)

### 왜 이게 중요한가

| 함수 | 산출물 | 그래프에서 |
|---|---|---|
| `fm_get` | `type` · `summary` · `created` | 노드 속성 |
| **`fm_list`** | **`builds_on` · `supersedes`** | **엣지** |

스키마 정본이 "이름 붙이는 관계는 둘뿐"이라고 못박은 그 둘. vault 전체에 `builds_on` 387개, `supersedes` 3개. 위키링크 24,969개가 전부 **무명** 엣지인 것과 대비되는, 유일하게 의미를 가진 관계다. Phase 8~9에서 추론의 재료가 되는 것도 이쪽.

### 할 일

`tests/test_frontmatter.py`의 import를 고치고

```python
from vault.frontmatter import fm_get, fm_list, split_frontmatter
```

파일 끝에 추가한다.

```python
LIST_FM = (
    "type: concept\n"
    "builds_on:\n"
    '  - "[[CIDR]]"\n'
    '  - "[[Subnet mask]]"\n'
    "created: 2026-08-10"
)


def test_reads_every_item_of_a_list_block():
    assert fm_list(LIST_FM, "builds_on") == ["CIDR", "Subnet mask"]


def test_returns_an_empty_list_for_a_missing_key():
    assert fm_list(LIST_FM, "supersedes") == []


def test_stops_at_the_next_key():
    fm = 'builds_on:\n  - "[[CIDR]]"\ntags:\n  - Stack/Python'
    assert fm_list(fm, "builds_on") == ["CIDR"]


def test_keeps_a_plain_item_that_is_not_a_wikilink():
    fm = "tags:\n  - Stack/Python\n  - Topic/Network"
    assert fm_list(fm, "tags") == ["Stack/Python", "Topic/Network"]


def test_an_inline_scalar_is_not_a_list():
    assert fm_list("builds_on: [[CIDR]]", "builds_on") == []
```

`uv run pytest -v` → 기존 10개 통과, 새 5개 `ImportError` 실패. **실패를 눈으로 본 뒤** GREEN으로 간다.

### 각 테스트가 검증하는 것

| 테스트 | 무엇을 | 왜 |
|---|---|---|
| `reads_every_item_of_a_list_block` | 정상 경로 | `[[ ]]`와 따옴표를 벗긴 알맹이를 돌려준다. 필요한 건 대상 이름이지 링크 문법이 아니다 |
| `returns_an_empty_list_for_a_missing_key` | 부재 | `supersedes`는 vault 전체에 3건. 대부분의 문서에서 대부분의 필드는 없다 |
| `stops_at_the_next_key` | 블록 경계 | 다음 키 항목까지 먹으면 `builds_on`에 태그가 섞이고 상한 3개 검사가 무의미해진다 |
| `keeps_a_plain_item_that_is_not_a_wikilink` | 링크 아닌 항목 | `tags:`도 같은 블록 문법인데 값이 링크가 아니다. 함수 하나로 둘 다 읽는다 |
| `an_inline_scalar_is_not_a_list` | 인라인 배제 | YAML은 `key: [a, b]`도 리스트지만 vault는 그렇게 안 쓴다. **지원하지 않기로 하고 그 결정을 테스트로 고정** |

### GREEN 힌트 (막힐 때만)

리스트 블록은 「키 줄 + 들여쓴 `- ` 줄들」이다. 다음 키를 만나면 끝난다. 정규식 하나로 블록을 통째로 잡고, 줄 단위로 쪼갠 뒤 `- `·따옴표·`[[ ]]`를 벗긴다. `fm_get`과 달리 **`re.M`과 여러 줄 매칭이 같이 필요하다.**

---

## 그 다음 — Step 4 실측

Phase 1의 마무리. 실제 vault 6,452개에 파서를 돌려 통계를 낸다.

- frontmatter 보유율 (`--- 로 시작` 90.4%는 근사치였다. `type` 값을 실제로 읽어 정확히 센다)
- `type` 분포 — 스키마 정본의 13값 밖에 있는 값이 있는가
- `builds_on` / `supersedes` 개수 — 답안지의 387 / 3과 대조
- `summary` 길이 분포 — 상한 80자를 넘는 게 몇 건인가

스크립트는 `tools/measure_phase01.py`에 남긴다. 커밋은 `feat(tools): …`.

이게 끝나면 **Phase 1 회고**를 쓰고(`learnings/phase01-*.md`) Phase 2로 넘어간다.

---

## 커밋 규칙 (Conventional Commits)

| 시점 | type | 예 |
|---|---|---|
| GREEN (테스트+구현 함께) | `feat` | `feat(frontmatter): fm_list — 리스트 블록 파싱` |
| REFACTOR | `refactor` | `refactor(frontmatter): 키 매칭 정규식을 헬퍼로 추출` |
| 기존 동작이 틀렸던 것 | `fix` | `fix(links): 표 안의 \| 가 타깃 끝에 역슬래시를 남기던 문제` |
| 실측 스크립트 | `feat(tools)` | `feat(tools): Phase 1 파서 실측` |
| Phase 가이드 | `docs` | `docs: Phase 2 가이드 — 위키링크 파서` |
| Q&A·회고 | `docs(learnings)` | `docs(learnings): Phase 1 회고` |

- RED는 커밋하지 않는다 — 실패 상태가 이력에 남으면 `git bisect`를 못 쓴다. GREEN 커밋에 테스트가 같이 들어가므로 명세는 보존된다
- GREEN과 REFACTOR를 **한 커밋에 섞지 않는다.** 섞으면 diff에서 "기능이 바뀐 건가 정리한 건가"를 읽을 수 없다
- 본문에는 **밟은 함정과 설계 결정**을 남긴다. 3개월 뒤 `git log`가 학습 노트가 된다

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
