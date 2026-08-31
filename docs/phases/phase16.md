# Phase 16 — SHACL 의미 계약

> OWL이 추론하는 것과 Vault가 요구하는 것을 분리한다.

## 목표

Phase 4의 Python lint가 문서 스키마를 검사하듯, SHACL은 의미 그래프의 구조와 필수
관계를 검사한다. OWL의 열린 세계 가정으로 표현할 수 없는 요구를 SHACL에 둔다.

초기 shape 후보:

- `Principle`은 승인된 근거를 최소 하나 가진다.
- `Decision`은 결과와 판단 근거를 가진다.
- `Claim`은 근거 artifact 위치를 가진다.
- `supersedes`의 주체와 대상은 같지 않다.
- `operationalizedBy`의 대상은 `Procedure`다.

## Step 1 — 기존 lint와 중복 범위를 정한다

기존 lint를 즉시 SHACL로 교체하지 않는다.

| 규칙 | 우선 구현 |
|---|---|
| frontmatter 날짜 형식 | Python lint 유지 |
| 위키링크 해석 | Python lint 유지 |
| RDF artifact에 abstract가 있는가 | parity 실험 |
| Principle의 evidence | SHACL 신규 |
| Decision의 semantic relation | SHACL 신규 |

같은 규칙을 양쪽에 구현할 때는 같은 fixture에서 결과가 일치해야 한다.

### 경계는 「무엇을 보는가」로 갈렸다 (2026-08-31)

```
lint    파일을 본다     →  그래프에 못 들어온 문서까지 본다
SHACL   그래프를 본다   →  타입이 붙은 뒤의 의미 구조를 본다
```

**「`type`이 없다」는 SHACL이 구조적으로 못 잡는다.** `type`이 없으면 `rdf:type`
트리플이 아예 안 생기고, shape는 클래스로 겨눈다. 실물이 하나 있다.

```
000 Index/Dots/2026-10 도쿄 여행 계획.md    type missing · created missing
```

경로에서 파생되는 `dcterms:isPartOf`로 겨누면 잡히긴 한다. **그런데 766개 폴더가
함께 걸린다.**

```sparql
SELECT ?d WHERE { ?d dcterms:isPartOf ?f . FILTER NOT EXISTS { ?d a ?c } }
→ 766   전부 폴더다
```

Phase 9가 `isPartOf`에 domain을 걸어 폴더 764개를 Document로 잘못 타입했던 **바로
그 자리**다. 그때는 추론, 이번엔 검증 타깃. **세 번째로 같은 경계에 걸렸고, 답도
같다 — `isPartOf`는 문서와 폴더가 공유한다.**

**그래서 lint를 SHACL로 교체하지 않는다.** 겹치는 규칙은 하나뿐이고 그것이 parity
시험이 된다.

| 규칙 | 구현 | 실측 |
|---|---|---|
| `type` 있음 · 값이 어휘 안 | **Python lint 전용** | SHACL이 못 본다 |
| `created` 있음 · 날짜로 파싱됨 | **Python lint 전용** | 위와 같은 문서 |
| 위키링크 해석 | **Python lint 전용** | 깨진 링크 369건 |
| 판단 구간에 `summary` | **양쪽 — parity** | 둘 다 **22건** |
| 의미 관계의 구조 | **SHACL 신규** | 아래 |

### 후보 아홉을 재고 다섯을 남겼다

「사람이 실제로 고칠 의향이 있는 규칙만」이 이 Phase의 지침이다. 위반율이 그것을
그대로 말해 준다.

```
0%        이미 지키고 있다        →  Violation 으로 걸 수 있다
2~6%      고칠 만한 부채          →  Violation.  22건은 고치면 된다
60~87%    구조적 부채             →  Warning.  거부하면 아무것도 못 쓴다
100%      규칙이 아니라 관측       →  기각
아무도 안 정함                    →  기각
```

| | shape | 위반 | 등급 |
|---|---|---|---|
| V1 | 의미 관계가 자기를 안 가리킨다 | **0** | Violation |
| V2 | 판단 구간(concept·procedure·reference·case)에 `summary` | **22 / 1,008** | Violation |
| V3 | 섹션은 자기 문서의 fragment다 | **0 / 324** | Violation |
| W1 | `PrincipleDocument`에 근거가 있다 | **43 / 94** | Warning |
| W2 | `DecisionDocument`에 근거가 있다 | **30 / 46** | Warning |
| W3 | 의미 관계가 해석됐다 (`_raw`가 아니다) | **17** | Warning |

**V1은 위반 0이라서 Violation으로 걸 수 있다.** 이미 지키고 있는 규칙만 강하게
걸 수 있다는 것이 이 표의 요지다. 그리고 V1은 빈 규칙이 아니다 — 2026-08-26에
기계 규칙이 `derived_from`을 자기 자신에 붙인 것이 **2건** 있었고 손으로 잡았다.
**그때 이 shape가 있었으면 기계가 잡았다.**

W3의 17건은 전부 `derived_from: experience`다. 깨진 게 아니라 **문서가 아닌 출처**를
가리키는 의도된 값이고, 이 Warning이 그것을 계속 눈에 띄게 해서 **별도 값이
필요한지를 개수로 판정**하게 한다 (Phase 15 Round 6의 미결).

#### 기각한 셋

```
Insight 에 as_of 필수        73/121   아무도 정한 적 없는 규칙이다.  만들면 내가 만든 부채다
Question 에 answered_by 필수  56/56   100%는 규칙이 아니라 「answered_by 를 안 쓴다」는 관측이다
answered_by 의 주체는 Question    0    용례가 0건이라 검사할 것이 없다.  domain 이 이미 말한다
```

#### 헛것을 세는 shape를 하나 잡았다

처음 쓴 「모든 문서에 `created`가 있다」가 위반 0을 냈다. **모집단도 0이었다.**

```sparql
?d a ?c . ?c rdfs:subClassOf* v:Document      → 0건
```

`.vault.ttl`에는 온톨로지가 안 실려 있어서 `subClassOf`가 한 건도 없다. **아무것도
검사하지 않은 shape가 깨끗하다고 보고한다.** Phase 9의 「아무것도 추론 못 하는
선언」과 같은 것이 검증 쪽에도 있다 — **shape마다 모집단을 함께 재는 것이 규칙이다.**

## Step 2 — shape를 RED 테스트로 작성한다

각 shape에 네 fixture를 둔다.

1. 통과하는 최소 그래프
2. 필수 값이 빠진 그래프
3. 타입이 잘못된 그래프
4. 경계값 또는 예외 그래프

위반 경로, severity, 사람이 읽는 메시지까지 테스트한다.

### 28개 fixture (2026-08-31)

`vault-shapes.ttl` 여섯 shape에 손으로 만든 그래프 28개. **fixture가 규칙의 뜻이고,
실제 vault는 그 뜻이 몇 건에 걸리는지만 말한다.**

경계값을 셋 적어 둔다.

```python
test_a_structural_link_to_itself_is_not_this_shapes_business
    links_to 는 본문이다.  자기 이름을 인용한 문서는 기계가 낸 오류가 아니다

test_an_empty_summary_is_still_a_summary
    SHACL 은 트리플을 센다.  내용이 있느냐는 Python lint 의 `summary too long` 쪽이다

test_a_prefix_match_is_not_enough
    `.../A` 와 `.../A 부록` 은 앞부분이 같다.  `#` 을 안 요구하면 남의 섹션이 통과한다
    — `인사이트 1` 이 `인사이트 10` 에 걸리던 것과 같은 실수다
```

### 조용한 실패 하나 — `sh:severity`의 자리

`sh:sparql` 블랭크 노드 **안에** 심각도를 적었더니 pyshacl이 **안 읽고 기본값
Violation으로** 보고했다. Warning으로 두려던 셋이 전부 Violation이었다.

```turtle
✗  sh:sparql [ sh:severity sh:Warning ; sh:select "…" ]
✓  sh:severity sh:Warning ;
   sh:sparql [ sh:select "…" ]
```

**무엇이 잡았나** — 등급별 fixture를 따로 둔 덕이다. `[f["severity"] for f in found]
== ["warning"]`가 `["violation"]`을 받고 깨졌다. 심각도를 안 세는 테스트였으면
「검사는 도는데 등급이 전부 틀린」 상태로 넘어갔을 것이고, **등급을 나누는 것이 이
Phase의 전부라서 그게 가장 비싼 실패였다.**

## Step 3 — 경고와 거부를 분리한다

- Violation: 승인 그래프에 들어갈 수 없음
- Warning: 들어갈 수 있으나 검토 필요
- Info: 개선 제안

처음부터 모든 shape를 거부 규칙으로 만들지 않는다. 기존 393개 lint 위반처럼 누적된
부채가 도입 자체를 막지 않도록 신규·변경 assertion과 전체 감사 모드를 구분한다.

### 감사 모드는 플래그 하나다

```
vault validate            violation 만 찍는다.  종료 코드 1
vault validate --audit    warning 까지 전부
```

부채 90건을 기본으로 쏟아내면 **아무도 끝까지 안 읽는다.** 그래서 기본은 거부
대상만 보이고, 마지막 줄이 warning이 몇 건 남아 있는지 알려 준다.

종료 코드는 **violation에만 걸린다.** warning이 90건이어도 0을 돌려주므로,
pre-commit이나 CI에 걸어도 기존 부채가 새 작업을 막지 않는다 — 이 Step이 요구한
바로 그것이다.

`--audit` 없이도 그래프는 **매번 새로 빌드한다.** 디스크의 `.vault.ttl`을 읽으면
방금 만든 위반이 안 보인다.

## Step 4 — SHACL 보고서를 원문에 연결한다

보고서는 IRI만 출력하지 않는다.

```text
문서 경로
section/block
위반한 지식 개체
shape와 메시지
관련 근거
수정 방향
```

### 한 줄이 곧 열 자리다

```
200 Dev Knowledge Base/…/monorepo VS polyrepo.md: [violation] 판단 구간 문서에 summary 가 없다 (…)
500 Mind Compiler/Q7. Who Am I/_Insights.md#인사이트 20: [violation] …
```

`section_path`가 IRI를 (경로, 제목 전문)으로 되돌리므로 **인사이트 24개짜리 파일에
대해 「이 파일 어딘가」라고 말하지 않는다.** Phase 15 Step 2의 「주체가 곧 출처」가
여기서 값을 한다 — 보고서에 따로 붙일 근거 자리가 필요 없었다.

정렬은 **심각도 → 경로 → 제목**이다. 사람이 위에서부터 읽고, 두 번 돌려도 같은
순서가 나온다.

노드 단위 제약은 초점 노드를 자기 값으로 보고하는데, 그걸 찍으면 경로를 IRI로 한 번
더 쓰는 것이라 **값이 초점 노드와 같으면 지운다.**

## Step 5 — 성능과 coverage를 측정한다

- 50개 gold set
- 500개 확대 표본
- 전체 Vault 파생 그래프

각 단계에서 실행 시간, 오탐, 누락, 위반 분포를 기록한다. 엔진 교체는 실제 병목이
나온 뒤에만 검토한다.

### 실측 (2026-08-31 · `tools/measure_phase16.py`)

```
gold set 50      트리플    526    0.21s   violation  1 · warning  4
확대 표본 500     트리플  4,070    0.87s   violation  9 · warning  8
전체 vault       트리플 28,436    3.54s   violation 22 · warning 90
```

**트리플이 54배 늘 때 시간은 17배 늘었다.** 병목이 없으므로 엔진을 안 건드린다.
비교값으로, 그래프를 만드는 데 1.86초가 걸린다.

```
shape 별      PrincipleNeedsGround 43 · DecisionNeedsGround 30
             JudgementNeedsSummary 22 · SemanticLinkShouldResolve 17
             NoSelfRelation 0 · SectionBelongsToItsDocument 0

parity        SHACL 22 · Python lint 22 · 일치
```

gold set 50개 중 **49개만 그래프에 있다.** 나머지 하나는
`900 Archive/Mind Compiler/_Insights.md`이고, D3이 900을 그래프에서 뺐다.
**누락이 아니라 설계다** — 그리고 그 문서가 gold set에 들어간 이유(C17이 지목)는
Phase 18의 질의가 900을 어떻게 다룰지의 문제로 남는다.

gold set에 걸린 다섯 건은 전부 **알고 있던 부채**다.

```
violation 1   0429_tdd_plan… 에 summary 가 없다        Python lint 의 22건 중 하나
warning 2     experience 두 건                        의도된 값
warning 2     _개발 규율집 · Decision Node 에 근거 없음   C04 가 잰 그 부채
```

**새로 만들어 낸 오탐이 0건이다.** 다섯 건 모두 이미 다른 자리에서 세어 둔 것을
다시 가리킨다.

### 세션 도중 vault가 움직였다

Step 1에서 `PrincipleDocument` 위반을 59/94로 쟀는데, Step 5에서 43/94가 나왔다.
`derived_from`이 69에서 160으로, `experience`가 2에서 17로 늘었다. **내가 쓴 것이
아니다 — vault 쪽에서 작업이 돌고 있었다.**

숫자를 현재값으로 고쳤고, 고치면서 확인한 것이 하나 있다. **이 저장소의 모든 실측은
스냅숏이고, 날짜가 붙어 있어야 한다.** `.vault.ttl`을 디스크에서 읽는 코드와 새로
빌드하는 코드가 서로 다른 답을 내는 것을 실제로 봤고, `vault validate`가 매번
새로 빌드하는 이유가 그것이다.

## 완료 판정 (2026-08-31)

| | |
|---|---|
| 초기 shape가 gold set의 기대 위반과 일치 | 5건 전부 이미 세어 둔 부채. **새 오탐 0** |
| 기존 lint와 겹치는 규칙은 결과가 일치 | **22 = 22** |
| OWA 추론과 닫힌 세계 검증이 분리 | `vault-ontology.ttl` / `vault-shapes.ttl`. 합치지 않는다 |
| 위반에서 원문 위치로 | `경로#제목`. `section_path` 왕복 |
| 기존 부채가 신규 assertion을 안 막는다 | 종료 코드는 violation 에만 걸린다. warning 90건은 0 |

## 산출물

- SHACL shapes 5개 이상
- shape fixture와 parity 테스트
- 사람이 읽는 검증 보고서
- 신규/변경 검증과 전체 감사 모드
- 성능·오탐·누락 측정

## 완료 조건

- [ ] 초기 shape가 gold set의 기대 위반과 일치한다.
- [ ] 기존 lint와 겹치는 규칙은 결과가 일치한다.
- [ ] OWA 추론과 닫힌 세계 검증이 코드와 문서에서 분리되어 있다.
- [ ] 위반에서 원문 위치로 바로 돌아갈 수 있다.
- [ ] 전체 Vault의 기존 부채가 신규 assertion 생성을 전부 막지 않는다.

## 난이도와 위험

**난이도: 중상. 기술보다 규칙 강도가 어렵다.**

SHACL 문법 자체보다 무엇을 필수로 볼지가 더 어렵다. 지나치게 강한 shape는 유효한
지식을 거부하고, 약한 shape는 형식만 갖춘 빈 데이터를 통과시킨다. 초기에는 실제로
사람이 수정할 의향이 있는 규칙만 넣는다.
