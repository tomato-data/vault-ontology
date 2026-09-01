# Phase 11 파일럿 — 문서 11개

> 2026-08-26 선정. 가이드는 [`phase11.md`](../phases/phase11.md), 어휘는 [`relations-v0.md`](../part3/relations-v0.md).
>
> **이 라벨링은 버려도 된다.** 목적은 데이터가 아니라 숫자 세 개다.

## 무엇을 재는가

```
1  문서 하나 라벨링에 몇 분 걸리는가
2  의미의 최소 단위가 문서인가 · 섹션인가 · 블록인가      ← 3부의 규모를 가른다
3  일주일 뒤 다시 라벨링하면 같은 답이 나오는가
```

2번이 [`part3-boundary.md`](../part3/boundary.md)의 분기 규칙을 결정한다.

---

## 문서 11개

각 문서에 **시험할 어휘**와 **왜 골랐는지**를 붙였다. 어휘 12개가 최소 한 번씩은
쓰이도록 짰다.

### 1 · 결정 두 개의 충돌

| | |
|---|---|
| 문서 | `400 Logic Forge/401 Architecture Playbook/Layer 2. Backend/Code-Structure/Decision Node - Pragmatic vs Clean Architecture.md` (70줄, 2026-02-07) |
| 시험 | `contradicts` · `derivedFrom` |
| 난점 | **다른 문서와 충돌** |

### 2 · 그 짝

| | |
|---|---|
| 문서 | `400 Logic Forge/401 Architecture Playbook/Layer 2. Backend/Architecture Style Selection/Decision Node - Architecture Style Selection.md` (110줄, 2025-12-06) |
| 시험 | `contradicts` |
| 난점 | 1번과 같은 선택지인데 팀 규모 임계값이 10명 대 5명이고 Hybrid 유무가 다르다. `supersedes` 없음 |

**이 둘이 `contradicts`를 실제 데이터로 시험할 유일한 자리다.**

### 3 · 근거 없는 원칙

| | |
|---|---|
| 문서 | `200 Dev Knowledge Base/299 Principles/Frontend/Frontend 테스트는 환경 부팅 비용을 먼저 측정하라.md` |
| 시험 | `derivedFrom` · `sourceUnknown` |
| 난점 | **밖에서 16회 인용되는데 근거 사건 링크가 없다.** 209에서 가장 많이 쓰이는 원칙 중 하나 |

### 4 · 그 원칙의 근거일 가능성

| | |
|---|---|
| 문서 | `300 Runtime/302 BNV Solutions/302.8 duoacademy/302.8.4. Learnings/Code Architecture/테스트 스위트 성능 — 측정 우선, 루프≠게이트, 검사량 축소.md` (160줄) |
| 시험 | `derivedFrom` · `applies` · `violates` |
| 난점 | 원칙 4개를 가리킨다. 그중 무엇이 「따랐다」이고 무엇이 「어겼다」인지 지금은 구분이 없다 |

**3번과 4번이 한 쌍이다.** 승격 계보가 실제로 이어지는지 본다.

### 5 · 저자에게서 온 원칙

| | |
|---|---|
| 문서 | `200 Dev Knowledge Base/299 Principles/Software Design/웹 개발자를 위한 소프트웨어 설계 원칙 (Ousterhout).md` |
| 시험 | `derivedFrom` · `divergesFrom` |
| 난점 | 저자의 주장을 그대로 옮긴 부분과 바꾼 부분이 섞여 있다 |

### 6 · 그 원본

| | |
|---|---|
| 문서 | `600 Content Observatory/601 Books/개발/A Philosophy of Software Design/A Philosophy of Software Design.md` (126줄, 대표노트) |
| 시험 | `divergesFrom` 의 대상 |
| 난점 | 챕터 22개의 대표노트다. 원칙이 **어느 챕터**에서 왔는지 가리키려면 문서보다 작은 단위가 필요할 수 있다 |

### 7 · 저자와 어긋난 기록

| | |
|---|---|
| 문서 | `400 Logic Forge/403 Case Studies/Case Study - Ousterhout의 TDD 비판과 ODP 통합 TDD의 대응.md` (63줄) |
| 시험 | `divergesFrom` · `contradicts` |
| 난점 | 5·6번과 한 계보다. 저자를 부정한 것인지 변형한 것인지 갈라야 한다 |

### 8 · 한 문서에 항목 다수

| | |
|---|---|
| 문서 | `500 Mind Compiler/Q1. Better Developer/_Insights.md` (155줄) |
| 시험 | `expresses` · `asOf` · `informs` |
| 난점 | **번호 매겨진 인사이트가 여럿 있다.** 하나를 가리키려면 문서 단위로는 안 된다 |

**이 문서가 측정 2번의 핵심이다.** 여기서 문서 단위로 충분한지 아닌지가 갈린다.

### 9 · 종결되어 보관된 질문

| | |
|---|---|
| 문서 | `900 Archive/Mind Compiler/_Question.md` (69줄, Q3) |
| 시험 | `status: archived` · `derivedFrom` · `asOf` |
| 난점 | 답이 확정된 채(v1.0, 2026-02-01) 900에 있고, 그 결론이 현재 Q7·Q2에서 살아 있다. **링크는 0** |

### 10 · 믿음이 시간에 따라 바뀐다는 기록

| | |
|---|---|
| 문서 | `100 Private Log/103 Debugger/103.1 Self/모든 정답은 일시적이다.md` (100줄, 2026-03-22) |
| 시험 | `asOf` · `expresses` |
| 난점 | **제목 자체가 「믿음은 일시적이다」**다. 시점 없는 사실로 적으면 그 자체가 틀린 기록이 된다 |

600에서 10회, 500에서 2회 인용된다. 콘텐츠를 보고 쓴 성찰이 다시 인용된다.

### 11 · 콘텐츠가 촉발한 성찰

| | |
|---|---|
| 문서 | `100 Private Log/103 Debugger/103.1 Self/시라트를 본 후 정호와의 대화.md` (96줄, 2026-02-23) |
| 시험 | `informs` · `derivedFrom` |
| 난점 | 영화 한 편이 대화와 성찰로 이어진 기록. `600 → 100 → 500` 흐름의 실물 |

`600/602 Frames/영화/Sirat.md`가 vault에서 9회 인용되는 문서다. C15가 승인된
질문의 정확한 사례다.

### 예비 — 극단 사례

`100 Private Log/103 Debugger/103.4 Work/BNV 솔루션.md` (331줄, 제목 33개).
100 대역에서 **밖에서 가장 많이 인용된다** — 300에서 14회. 개인 성찰이 프로젝트
판단에 닿는 사례이므로 C09에 딱 맞지만, 331줄이라 이 문서 하나가 시간 측정을
지배할 수 있다. **먼저 열 개를 끝낸 뒤, 여유가 있으면 붙인다.**

2026-08-26에 D4의 읽기 제한이 풀렸다. 위 두 문서로 재는 것은
**「개인 문서의 라벨링이 기술 문서와 얼마나 다른가」**다. 관점·시점·해석 변화가
얹히므로 비용 구조가 다를 수 있다. 사적 내용은 밖으로 옮기지 않는다 (D6) —
근거는 경로만 적고 인용하지 않는다.

---

## 대역 분포

```
200 Dev KB     2      개발 지식이 전체의 절반을 넘지 않는다
300 Runtime    1
400 Logic Forge 3
500 Mind Compiler 1
600 Content    1
900 Archive    1
100 Private Log 2
              ──
              11
```

phase11이 정한 8~10을 하나 넘는다. 3·4번과 5·6·7번이 각각 한 계보를 이루므로
쪼개면 시험이 성립하지 않는다. 개발 지식 대역(200)은 2개로 전체의 5분의 1이다.

## 어휘 커버리지

| 어휘 | 시험되는 문서 |
|---|---|
| `derivedFrom` | 1 · 3 · 4 · 5 · 9 · 11 |
| `contradicts` | 1 · 2 · 7 |
| `divergesFrom` | 5 · 6 · 7 |
| `applies` | 4 |
| `violates` | 4 |
| `informs` | 8 · 11 |
| `expresses` | 8 · 10 |
| `answeredBy` | 9 |
| `status: archived` | 9 |
| `sourceUnknown` | 3 |
| `asOf` | 8 · 9 · 10 |
| `needsReview` | — |

`needsReview`는 파일럿에서 안 나온다. **운영 상태라 라벨링이 아니라 계산으로
나오기 때문**이다. Phase 17에서 시험한다.

## 난점 커버리지

phase11이 「쉬운 것만 고르지 말라」며 요구한 여섯 가지 중 다섯이 들어 있다.

- ✅ 한 문서에 주장이 여러 개 — 8번
- ✅ 다른 문서와 충돌 — 1·2번
- ✅ 근거가 명시되지 않은 원칙 — 3번
- ✅ 과거와 현재의 해석이 다름 — 9번 · 10번
- ✅ 개인 경험이 개발·커리어 판단에 닿음 — 11번 (예비 문서가 더 강한 사례)
- ❌ `supersedes` 관계 — **vault에 5건뿐이고 전부 대상이 없어 시험할 수 없다**

마지막 항목이 없는 것 자체가 결과다. 「대체됨」이 이 vault에서 작동하지 않는다.
