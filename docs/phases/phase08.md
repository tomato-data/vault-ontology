# Phase 8 — 어휘 설계 (RDFS · OWL · SKOS)

> 산출물: `vault-ontology.ttl` · scope: `vocab`
> **여기가 "온톨로지"라는 단어가 실제 내용을 갖는 곳이다.**

## 큰 그림

Phase 6~7까지도 아직 온톨로지가 아니다. 트리플로 적힌 **데이터**일 뿐이다. 스키마는 여전히 코드 안에 있다 — `TYPES = {...}`, `if t not in TYPES: reject()`.

이 Phase에서 **스키마를 데이터로 옮긴다.**

```
Phase 4    TYPES = {"concept", "procedure", ...}      상수 · 코드
           if t not in TYPES: reject()                명령형

Phase 8    v:Concept a rdfs:Class .                   데이터 · 그래프
           v:type rdfs:range v:DocumentType .         선언형
```

이게 왜 다른가. **스키마가 그래프 안에 있으면 그래프 질의로 스키마를 물을 수 있고, 추론기가 읽을 수 있다.** 코드 안의 `set`은 둘 다 못 한다.

## 핵심 개념

### 1. 온톨로지 설계의 첫 규칙 — 남의 어휘를 쓴다

새 술어를 발명하기 전에 **이미 있는 표준 어휘를 찾는다.** 이유는 상호운용성이다. `dcterms:created`를 쓰면 세상의 모든 도구가 그게 생성 시각인 줄 안다. `v:created`는 나만 안다.

| 어휘 | 쓸 자리 |
|---|---|
| **RDFS** | 클래스·계층·`domain`/`range`·`label` |
| **OWL** | `TransitiveProperty` · `inverseOf` · 카디널리티 |
| **SKOS** | **개념 체계.** `Concept`·`broader`/`narrower`·`related`·`prefLabel` |
| **Dublin Core** (`dcterms:`) | `created`·`title`·`subject`·`references` |
| **FOAF** | 사람 — 이 vault에는 거의 불필요 |

**SKOS가 이 프로젝트에 특히 맞다.** 문서·주제·태그처럼 "느슨하게 위계가 있는 개념 모음"을 위해 만들어진 표준이다. 태그 체계(`Stack/Python` ⊂ `Stack`)가 정확히 `skos:broader`다.

> 아무 표준도 안 쓰고 전부 자기 술어로 만드는 것 — 흔한 초보 실수다. 그러면 그건 "온톨로지"가 아니라 그냥 사설 스키마다.

### 2. RDFS — 클래스와 계층

```turtle
v:Document      a rdfs:Class .
v:Concept       a rdfs:Class ; rdfs:subClassOf v:Document .
v:Procedure     a rdfs:Class ; rdfs:subClassOf v:Document .
```

> **Phase 13에서 개명했다.** 리프 13종은 지금 `v:ConceptDocument`처럼 접미를
> 갖는다. 접미 없는 이름은 지식 개체 몫이다. 이 문서는 Phase 8 당시의 기록이라
> 그대로 둔다 — [`phase13.md`](phase13.md) Step 1 참고.

**여기서 이 Phase의 핵심 질문이 나온다.**

> vault의 `type` 13가지 값에 실제로 계층이 있는가?

지금은 **평평한 집합**이다. 13개가 나란히 있다. 하지만 스키마 정본의 정의를 다시 읽으면 묶음이 보인다.

```
이해가 목적          concept · procedure · reference
지키는 규칙          principle
특정 시점의 기록      decision · case · log · reflection
남에게서 온 것        capture
구조                 hub · template
프로젝트             project-doc · tradeoff
```

**이게 진짜 계층인지, 아니면 사후에 갖다 붙인 이야기인지**를 판정하는 것이 이 Phase의 산출물이다. 판정 기준은 하나여야 한다.

> **상위 클래스로 묶으면 답할 수 있게 되는 질의가 있는가?**

없으면 계층을 만들지 않는다. 「필요한 질의가 없으면 안 넣는다」는 스키마 정본의 원칙이 여기서도 적용된다. **"계층이 없다"고 결론내는 것도 정당한 답이다.**

### 3. domain과 range — 그리고 함정

```turtle
v:builds_on  rdfs:domain v:Document ;
             rdfs:range  v:Document .
```

읽는 법: "`builds_on`의 주어는 Document이고 목적어도 Document다."

**이게 검증 규칙처럼 보이지만 아니다.** RDFS에서 `domain`/`range`는 **추론 규칙**이다.

```
X v:builds_on Y  가 있으면
  →  X a v:Document  를 추론한다 (검사하는 게 아니라 만들어낸다)
```

Phase 4의 lint와 정반대 방향이다. lint는 "Document가 아니면 거부", RDFS는 "그렇다면 Document인 것이다"라고 처리한다. Phase 9에서는 너무 넓은 `dcterms:isPartOf` domain 때문에 **폴더 764개가 `v:Document`로 추론되는 문제**를 실제로 확인했다.

### 4. OWL — 관계의 성질을 선언한다

```turtle
v:builds_on  a owl:TransitiveProperty .
v:links_to   a owl:ObjectProperty .
v:linked_by  owl:inverseOf v:links_to .
```

| 선언 | 의미 | Phase 5·7에서는 |
|---|---|---|
| `TransitiveProperty` | A→B, B→C면 **A→C다** | 재귀 CTE / `+`로 **질의할 때마다** 계산 |
| `inverseOf` | A links_to B면 **B linked_by A다** | `UNION ALL` / `^`로 **질의할 때마다** |
| `SymmetricProperty` | 양방향 | 해당 없음 |

차이가 뭔가. **질의의 성질이 아니라 관계 자체의 성질로 선언한다.** 그러면 추론기가 트리플을 실제로 만들어내고, 그 뒤로는 아무 질의나 그 사실을 볼 수 있다.

**대가가 있다.** 트리플이 폭발한다. `builds_on` 387개가 이행 폐쇄를 물질화하면 몇 개가 되나 — Phase 9에서 잰다.

### 5. 온톨로지가 아닌 것

경계를 분명히 해둔다. 이걸 혼동하면 나중에 판단이 흐려진다.

| | 형식 의미론 | 추론기 | 이 프로젝트 |
|---|---|---|---|
| 속성 그래프 (Neo4j) | ✗ | ✗ | Phase 5 |
| RDF 데이터만 | ✗ | ✗ | Phase 6~7 |
| **RDFS/OWL 어휘 + 추론** | **✓** | **✓** | **Phase 8~9** |

업계에서 "온톨로지"를 넓게 쓰는 건 흔하다. 하지만 **형식 의미론과 추론이 있느냐**가 실제 구분선이다.

---

## Step 목록

| Step | 내용 |
|---|---|
| 1 | 표준 어휘 조사 — SKOS·Dublin Core에서 재사용할 것 목록 |
| 2 | `type` 13가지 값의 클래스 계층 **판정** (있으면 설계, 없으면 없다고 결론) |
| 3 | 태그 체계 → `skos:broader` (`Stack/Python` ⊂ `Stack`) |
| 4 | 속성 선언 — `domain`·`range`·`TransitiveProperty`·`inverseOf` |
| 5 | `vault-ontology.ttl` 작성 · rdflib로 로드 검증 |
| 6 | 어휘 문서화 — 각 술어가 **어떤 질의에 답하는가** |

---

## 완료 기준

- [x] `vault-ontology.ttl`이 데이터와 **별도 파일**로 존재한다 (스키마와 데이터의 분리)
- [x] 표준 어휘(SKOS·dcterms)를 **실제로 재사용**했다 — 전부 자기 술어면 실패
- [x] `type` 계층 질문에 **답을 냈다** — 있다면 근거 질의, 없다면 왜 없는지
- [x] 태그 계층이 `skos:broader`로 표현됐다
- [x] 모든 술어에 "어떤 질의에 답하나"가 적혀 있다 — 못 적으면 그 술어는 지운다
