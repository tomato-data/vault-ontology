# Phase 8: Q&A

> 어휘 설계. 스키마를 코드에서 데이터로 옮긴다. 여기서 "온톨로지"가 내용을 갖는다.

## Step 1 결정 — 재사용할 표준 어휘

남의 어휘를 먼저 찾는다. 정한 매핑.

| 우리 술어 | 표준 | 방식 |
|---|---|---|
| `v:created` | `dcterms:created` | 교체 |
| `v:part_of` | `dcterms:isPartOf` | 교체 |
| `v:supersedes` | `dcterms:replaces` | 교체 (방향까지 일치) |
| `v:tagged` | `dcterms:subject` | 교체 (문서 → `skos:Concept`) |
| `v:summary` | `dcterms:abstract` | 교체 |
| `v:builds_on` | `dcterms:references` | `v:` 유지 · `rdfs:subPropertyOf` 로 매담 |
| `v:links_to` | `dcterms:references` | `v:` 유지 · `rdfs:subPropertyOf` 로 매담 |
| `v:hub` | `foaf:primaryTopic` | `v:` 유지 · `rdfs:subPropertyOf` 로 매담 |
| `skos:broader` | — | Phase 6에서 이미 표준 |

### 왜 다 교체하지 않나

`builds_on`·`links_to`·`hub`는 이 vault 고유의 관계다. 정확히 맞는 표준이
없다. 억지로 표준에 욱여넣지 않고, **고유 이름을 두되 표준의 하위 속성**
으로 매단다.

```turtle
v:builds_on  rdfs:subPropertyOf  dcterms:references .
```

이러면 references를 아는 도구가 builds_on도 references로 읽는다. 고유성과
상호운용성을 동시에 얻는다. "전부 표준"도 "전부 자기 것"도 아닌 중간이
맞는 답이다.

### dcterms:subject 가 태그를 표준에 잇는다

`v:tagged` → `dcterms:subject` 로 바꾸면, 이미 `skos:Concept` 인 태그를
문서가 "주제로 삼는다"가 된다. SKOS 표준이 상정한 바로 그 그림이다.
문서 → dcterms:subject → skos:Concept → skos:broader → 상위 개념.

## Step 2 판정 — type 계층은 "역할" 3개다

기준: 상위 클래스로 묶어야 답할 수 있는 질의가 있는가.

가이드가 제안한 **6개 의미 묶음**(이해/규칙/기록/출처/구조/프로젝트)은
대부분 사후 서사였다 — concept·procedure·reference를 한 덩어리로 물을 일이
없다. 각각 따로 본다.

진짜 구분선은 의미가 아니라 **역할**이었다. `source-note`가 전체의 31%라는
게 실마리였다.

```
v:Document                          최상위
  v:Content     내가 쓴 실제 내용    concept·procedure·reference·principle·
                                    decision·case·log·reflection·project-doc·tradeoff
  v:Imported    남에게서 온 것        source-note
  v:Structural  뼈대, 내용 아님       hub·template
```

이 계층이 버는 질의:

- "내가 쓴 원본 사고만" = `?d a v:Content` (Imported·Structural 제외)
- "실제 내용 노트 수" = Structural 빼고 세기

Phase 7 orphans 에서 hub가 낀 게 실은 이 문제였다 — 내용과 뼈대를 안
갈랐던 것. 3역할 계층이 그 구분을 스키마에 새긴다.

6개 의미 묶음은 문서에 남기되 계층으로는 만들지 않는다. "계층이 없다"가
그 묶음들에 대한 정당한 답이다.

## Step 4 결정 — 속성의 성질

### 4-1. domain·range 는 검증이 아니라 추론이다

각 속성의 주어·목적어 타입을 선언한다.

| 속성 | domain | range |
|---|---|---|
| `v:builds_on` | `v:Content` | `v:Content` |
| `v:links_to` | `v:Document` | `v:Document` |
| `dcterms:replaces` | `v:Document` | `v:Document` |
| `dcterms:isPartOf` | `v:Document` | `v:Folder` |
| `dcterms:subject` | `v:Document` | `skos:Concept` |
| `v:hub` | `v:Folder` | `v:Document` |

**함정을 반드시 기억한다.** RDFS domain/range 는 검사가 아니라 추론이다.
`X v:builds_on Y` 가 있으면 추론기가 `X a v:Content` 를 **만들어낸다**.
Phase 4 lint 는 "Content 아니면 거부", RDFS 는 "그러니 Content 다".
방향이 반대다. Phase 9 에서 타입 없던 문서가 이렇게 Content 가 되는 걸 본다.

### 4-2. transitive·inverse 는 선언만, 물질화는 Phase 9

| 선언 | 뜻 |
|---|---|
| `v:builds_on a owl:TransitiveProperty` | A→B, B→C ⇒ A→C |
| `v:linked_by owl:inverseOf v:links_to` | A→B ⇒ B linked_by A |

**결정: 둘 다 vault-ontology.ttl 에 선언하되, 데이터에는 아직 추론을
돌리지 않는다.** 선언(스키마)과 추론(폭발)을 분리한 채로 둔다. Phase 9 가
그 차이를 보여주는 실험이다 — builds_on 415개가 이행 폐쇄로 몇 개가 되나,
역링크 8,292개가 물질화되면 어떻게 되나.

builds_on 을 transitive 로 선언하는 건 Phase 6 의 큐레이션 의도(직접 선행만
추림)와 반대 방향이다. 그래도 선언해두는 이유는 Phase 9 에서 **큐레이션과
추론이 충돌하는 지점**을 실제로 보기 위해서다. 선언이 곧 물질화는 아니므로,
Phase 9 전까지 데이터는 지금 그대로다.
