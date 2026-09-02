# Phase 8: Q&A

> 어휘 설계. 스키마를 코드에서 데이터로 옮긴다. 여기서 "온톨로지"가 내용을 갖는다.

## Step 1 결정 — 재사용할 표준 어휘

새 술어를 만들기 전에 재사용할 수 있는 표준 어휘를 먼저 찾았다. 최종 매핑은 다음과 같다.

| 우리 술어 | 표준 | 방식 |
|---|---|---|
| `v:created` | `dcterms:created` | 교체 |
| `v:part_of` | `dcterms:isPartOf` | 교체 |
| `v:supersedes` | `dcterms:replaces` | 교체 (방향까지 일치) |
| `v:tagged` | `dcterms:subject` | 교체 (문서 → `skos:Concept`) |
| `v:summary` | `dcterms:abstract` | 교체 |
| `v:builds_on` | `dcterms:references` | `v:` 유지 · `rdfs:subPropertyOf`로 연결 |
| `v:links_to` | `dcterms:references` | `v:` 유지 · `rdfs:subPropertyOf`로 연결 |
| `v:hub` | `foaf:primaryTopic` | `v:` 유지 · `rdfs:subPropertyOf`로 연결 |
| `skos:broader` | — | Phase 6에서 이미 표준 |

### 왜 다 교체하지 않나

`builds_on`·`links_to`·`hub`는 이 vault 고유의 관계다. 정확히 맞는 표준이
없다. 의미가 맞지 않는 표준 술어로 대체하지 않고, **고유 이름을 유지하되 표준의 하위 속성**
으로 연결한다.

```turtle
v:builds_on  rdfs:subPropertyOf  dcterms:references .
```

이렇게 하면 `references`를 이해하는 도구가 `builds_on`도 참조 관계로 해석할 수 있다.
고유한 의미와 상호운용성을 함께 보존하는 방식이다.

### dcterms:subject가 태그를 표준에 잇는다

`v:tagged` → `dcterms:subject`로 바꾸면, 이미 `skos:Concept`인 태그를
문서가 해당 개념을 주제로 삼는다는 뜻이 된다. SKOS가 의도한 모델과도 맞는다.
문서 → dcterms:subject → skos:Concept → skos:broader → 상위 개념.

## Step 2 판정 — type 계층은 "역할" 3개다

기준: 상위 클래스로 묶어야 답할 수 있는 질의가 있는가.

가이드가 제안한 **6개 의미 묶음**(이해/규칙/기록/출처/구조/프로젝트)은
대부분 구현 결과를 사후에 설명하기 위한 묶음이었다. concept·procedure·reference를
한꺼번에 조회할 실제 요구가 없었기 때문이다.

진짜 구분선은 의미가 아니라 **역할**이었다. `capture`가 전체의 31%라는
게 실마리였다.

```
v:Document                          최상위
  v:Content     내가 쓴 실제 내용    concept·procedure·reference·principle·
                                    decision·case·log·reflection·project-doc·tradeoff
  v:Imported    남에게서 온 것        capture
  v:Structural  뼈대, 내용 아님       hub·template
```

이 계층으로 가능해지는 질의:

- "내가 작성한 내용만" = `?d a v:Content` (Imported·Structural 제외)
- "실제 내용 노트 수" = Structural 빼고 세기

Phase 7의 고아 노트 결과에 hub가 포함된 이유도 내용과 구조를 구분하지 않았기 때문이다.
3역할 계층은 이 차이를 스키마에 명시한다.

6개 의미 묶음은 문서에 남기되 계층으로는 만들지 않는다. "계층이 없다"가
그 묶음들에 대한 정당한 답이다.

## Step 4 결정 — 속성의 성질

### 4-1. domain·range는 검증이 아니라 추론이다

Phase 8에서 처음 선언한 주어·목적어 타입은 다음과 같다. Phase 9 실측 뒤
`dcterms:isPartOf`의 domain은 제거했다.

| 속성 | domain | range |
|---|---|---|
| `v:builds_on` | `v:Content` | `v:Content` |
| `v:links_to` | `v:Document` | `v:Document` |
| `dcterms:replaces` | `v:Document` | `v:Document` |
| `dcterms:isPartOf` | ~~`v:Document`~~ 제거 | `v:Folder` |
| `dcterms:subject` | `v:Document` | `skos:Concept` |
| `v:hub` | `v:Folder` | `v:Document` |

**함정을 반드시 기억한다.** RDFS domain/range는 검사가 아니라 추론이다.
`X v:builds_on Y`가 있으면 추론기가 `X a v:Content`를 **만들어낸다**.
Phase 4 lint는 "Content가 아니면 거부", RDFS는 "그러니 Content다"라고 처리한다.
방향이 반대다. Phase 9에서는 같은 원리로 폴더 764개가 Document로 잘못 추론되는 문제를 확인했다.

### 4-2. `transitive`·`inverse`는 먼저 선언하고 Phase 9에서 물질화한다

| 선언 | 뜻 |
|---|---|
| `v:builds_on a owl:TransitiveProperty` | A→B, B→C ⇒ A→C |
| `v:linked_by owl:inverseOf v:links_to` | A→B ⇒ B linked_by A |

**결정: 둘 다 `vault-ontology.ttl`에 선언하되, 데이터에는 아직 추론을
적용하지 않는다.** 선언과 물질화를 분리해 Phase 9에서 증가량을 측정했다.
`builds_on`은 415개에서 718개로, 역링크는 0개에서 8,292개로 늘었다.

`builds_on`을 transitive로 선언하는 것은 직접 선행 관계만 남긴 Phase 6의
큐레이션 의도와 긴장 관계에 있다. Phase 9에서는 이를 실제로 물질화해
**큐레이션과 추론이 충돌하는 지점**을 확인했다.
