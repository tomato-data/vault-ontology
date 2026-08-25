# Phase 1 — frontmatter 파서

## 큰 그림

vault 문서의 맨 앞 `---` 블록에는 `type`, `summary`, `builds_on`, `created`가 들어 있다. **그래프의 노드 속성과 명시적 관계가 모두 여기서 나온다.** 이 정보를 읽지 못하면 이후 Phase를 진행할 수 없다.

이번 Phase의 산출물은 함수 세 개다.

```
split_frontmatter(text)  →  (frontmatter 문자열 | None, 본문)
fm_get(fm, key)          →  스칼라 값 | None          type · summary · created
fm_list(fm, key)         →  값 목록                    builds_on · supersedes · tags
```

## 이전 Phase와의 연결

첫 Phase이므로 앞선 단계는 없다. 대신 **이 함수들이 이후에 어떻게 쓰이는지**를 알고 시작한다.

| 나중에 | 쓰는 함수 |
|---|---|
| Phase 2 | `split_frontmatter` — 본문만 골라 위키링크를 센다. frontmatter의 `builds_on`을 링크로 또 세면 이중 계산이다 |
| Phase 4 | `fm_get`·`fm_list` — 스키마 위반 검출 |
| Phase 5 | 셋 다 — 노드 속성과 `builds_on` 엣지 |
| Phase 6 | 셋 다 — 트리플의 술어(predicate)와 목적어(object) |

## 핵심 개념

### 1. YAML을 정규식으로 파싱한다는 결정

표준 라이브러리에 YAML 파서가 없다. 선택지는 셋이다.

| 선택 | 대가 |
|---|---|
| PyYAML 의존성 추가 | 완전한 YAML. 하지만 vault의 frontmatter는 YAML 전체를 쓰지 않는다 |
| **정규식으로 부분집합 파싱** | 가볍다. **깨지는 지점을 내가 알아야 한다** |
| 직접 YAML 파서 작성 | 이 프로젝트의 목적이 아니다 |

Phase 1~5는 **표준 라이브러리만** 쓴다 (기존 `vault.py`의 불변식이자, 파서를 손으로 짜는 게 학습의 핵심이라서). Phase 6에서 `rdflib`가 들어오면서 이 제약은 의도적으로 푼다.

정규식 파싱을 고르면 **어디서 깨지는지 아는 것이 의무가 된다.** 그 목록을 만드는 것이 이번 Phase의 진짜 산출물이다.

### 2. 정규식에서 `\s`는 개행을 먹는다

기존 `vault.py`가 실제로 밟은 지뢰다.

```python
re.search(r"^summary:\s*(.+)$", fm, re.M)
```

`summary:`가 비어 있으면 `\s*`가 개행을 넘어가 **다음 줄을 summary 값으로 읽는다.** `[ \t]*`로 좁혀야 한다.

`re.M`(MULTILINE)에서 `^`와 `$`는 줄 단위로 붙지만, `\s`는 여전히 `\n`을 포함하는 문자 클래스다. 이 둘이 어긋난다.

### 3. `re.S`(DOTALL)와 비탐욕 매칭

frontmatter는 `---`로 시작해 `---`로 끝난다. 그 안에 개행이 있으므로 `.`이 개행을 먹어야 하고(`re.S`), 본문에도 `---`가 있을 수 있으므로 **첫 번째 닫는 `---`에서 멈춰야 한다**(`.*?` 비탐욕).

```
---              ← 여는 구분자. 반드시 파일 맨 앞
type: concept
---              ← 여기서 멈춰야 한다
# 제목
---              ← 본문의 수평선. 여기까지 먹으면 안 된다
```

---

## Step 목록

| Step | 함수 | 핵심 함정 |
|---|---|---|
| 1 | `split_frontmatter` | 본문의 `---` · frontmatter 없는 문서 · 파일 중간의 `---` |
| 2 | `fm_get` | 빈 값이 다음 줄을 먹는 문제 · 값 안의 `:` · 따옴표 |
| 3 | `fm_list` | 리스트 블록 인식 · `[[...]]` 벗기기 · 빈 리스트 |
| 4 | 실측 | 실제 vault 6,289개에 돌려 통계를 낸다 |

---

## 완료 기준

- [x] `uv run pytest -v` 전부 통과 — 16개
- [x] Step 4 실측이 돌아간다 — `tools/measure_phase01.py`
- [x] `type` 분포가 스키마 정본의 13값 안에 들어온다 — 제외 후 정확히 13개. 제외 전에는 `800 TRPG`의 5값 1,822건이 섞인다
- [x] "정규식 파싱이 깨지는 지점" 목록을 `learnings/phase01-qa.md`에 적었다

**Phase 1 완료 (2026-08-18).** 회고는 [`learnings/phase01-measure-then-decide.md`](../learnings/phase01-measure-then-decide.md).
