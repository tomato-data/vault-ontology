# Phase 14 — 핵심 도메인 온톨로지 0.1

> 문서 구조가 아니라 Vault가 다루는 지식 세계를 최소 어휘로 명세한다.

## 목표

Phase 10의 역량 질문과 Phase 13의 정체성 계약을 바탕으로 작은 TBox를 만든다.
개발 지식 전용 스키마가 아니라 Vault 전체가 공유할 **영역 중립 kernel**과, 필요한
영역에서만 붙는 vocabulary/profile의 경계를 설계한다.
후보는 다음과 같지만 질문에 쓰이지 않는 것은 넣지 않는다.

```text
KnowledgeArtifact
Concept
Claim
Event
Decision
Principle
Procedure
Project
```

개인 경험·성찰·철학 표본을 검토한 뒤 다음 후보가 독립 클래스인지 상태·관계인지
판정한다.

```text
Belief · Value · Question · Interpretation · PersonalExperience
```

기술적 `Claim`과 개인적 `Belief`는 모두 문장으로 표현될 수 있지만 진리 조건이
다르다. 개인적 생각에는 주체·관점·시점·경험 맥락을 보존하고, 객관적 사실처럼
무맥락하게 전파하지 않는다.

관계 후보:

```text
expresses · supports · contradicts · derivedFrom · observedIn
appliesTo · requires · operationalizedBy · supersedes
invalidates · hasEvidence · affects
```

## Step 1 — 어휘 요구사항을 질문에서 역추적한다

각 클래스와 속성에 다음을 기록한다.

- 어떤 역량 질문이 이것을 요구하는가
- 자연어 정의와 포함·제외 사례
- 정의역과 치역
- 반례
- 표준 어휘를 재사용하지 않은 이유
- 예상되는 추론

질문이 하나도 연결되지 않는 어휘는 삭제한다.

### 결과 — 후보 13개 중 11개가 삭제됐다 (2026-08-26)

#### 먼저 잰 것 — `type: reflection` 하나가 세 가지를 담고 있다

```
By Subquestion/*.md     27문서   제목이 곧 질문   "결혼은 하고 싶은가?"
_Insights.md             7문서   인사이트 130항목
_Patterns.md             7문서   패턴 항목
                                 전부 type: reflection
```

**문서 클래스로는 못 가른다.** Phase 13이 문서와 지식 개체를 갈라놓은 자리가 여기서
실물로 나타난다. 그리고 vault는 이미 항목의 종류를 **한국어 접두로 적고 있다.**

```
패턴      135항목 · 32문서   300 Runtime · 기술적 해법
인사이트   130항목 ·  7문서   500·900 · 주체와 시점이 있는 통찰
교훈       29항목 · 20문서   300 Runtime · 경험의 일반화
사례       21항목 ·  7문서   200 Dev KB · 증거
규칙 4 · 원칙 4              각각 한 문서뿐
```

문서의 `type`이 그 안의 항목이 무엇인지 말해주지 않는다 — `procedure` 안에 `원칙`이,
`project-doc` 안에 `패턴`이, `principle` 안에 `사례`가 들어 있다.

#### 삭제 규칙을 그대로 적용한 결과

```
KnowledgeArtifact   삭제   v:Document 가 이미 그것
Concept             삭제   C25가 「기존 도구」 판정
Claim               삭제   vault에 대응물 없음. 기술 주장은 「패턴」으로 적힌다
Event               삭제   v:CaseDocument
Decision·Principle·Procedure·Project   삭제   전부 문서 클래스로 있다
Interpretation      삭제   실물 없음
PersonalExperience  삭제   100 Private Log 문서가 그것
Value               보류   C07이 요구하는데 「가치」로 적힌 항목이 0개다

Belief              ✅ v:Insight 로 채택   C08 · C07 — vault가 쓰는 말이 「인사이트」
Question            ✅ v:Question 채택      C27 — 실물 27문서
```

**관측 5의 숙제에 답이 나왔다.** `Claim`을 넣을 근거가 없다 — vault의 기술 주장은
`Claim`이 아니라 `패턴`으로 적힌다. `Tradeoff`는 뺄 이유가 없고 이미
`v:TradeoffDocument`로 있다.

#### 규칙이 걸린 자리 — `패턴` 135개를 요구하는 질문이 없다

```
v:Insight    C08 · C07        남는다
v:Question   C27              남는다
v:Pattern    요구하는 질문 없음   ← vault에서 제일 많은데 삭제 대상
v:Lesson     C28이 스칠 뿐
```

**vault에서 가장 많은 지식 개체를 어떤 역량 질문도 요구하지 않는다.** 읽는 방법이 둘.

```
(a) 질문 30개가 300 Runtime의 기술 패턴을 안 다룬다   → 질문 쪽의 공백
(b) 패턴은 문서 내용이지 온톨로지가 아니다            → 클래스 불필요
```

**(a)로 본다.** 질문 30개가 400·200·500에 몰려 있고 300을 주어로 하는 것이 거의 없다.
그래도 **넣지 않는다** — 규칙을 어길 근거가 없고 넣지 않아도 손해가 없다. 섹션은
`v:Section`으로 존재하고, **지식 개체 클래스는 질문이 요구할 때만 붙는다.**

이건 삭제가 아니라 **기록된 공백**이다. 질문이 생기면 그때 넣는다.

#### Step 1이 남기는 kernel

```
문서 클래스     Phase 13에서 확정. 새로 만들지 않는다
v:Section      Phase 13 Step 4
v:Insight      C08 · C07
v:Question     C27
```

관계는 [`../part3/relations-v0.md`](../part3/relations-v0.md)의 8개 + 섹션을 잇는
술어 하나(Step 2에서 `dcterms:hasPart`로 확정). 상한(클래스 8~12 · 관계 10~15)
안이고, **상한은 목표가 아니다** (관측 7 — 순수 온톨로지 질문이 3개다).

#### 표기 — `snake_case` 로 통일했다

```
relations-v0.md        derivedFrom · sourceUnknown · asOf     camelCase   ← 어긋나 있었다
semantic-authoring.md  derived_from · source_unknown · as_of  snake_case
파일럿 실사용           answered_by                            snake_case
```

`vault-ontology.ttl`이 이미 `v:builds_on`으로 RDF의 `camelCase` 관례를 벗어나 있다.
`snake_case`로 맞추면 **frontmatter 키와 RDF 이름이 같은 문자열**이 되어 변환표가
없어진다. 변환표는 조용히 어긋나는 자리다.

## Step 2 — 표준 어휘 재사용 범위를 정한다

우선 검토:

- Dublin Core Terms — 문서 메타데이터와 참조
- SKOS — 느슨한 주제·개념 체계
- PROV-O — Entity·Activity·Agent와 출처 계보
- OWL/RDFS — 클래스·속성·논리 공리

표준과 이름이 비슷하다는 이유만으로 재사용하지 않는다. 실제 의미와 제약이 맞는지
확인하고, 맞지 않으면 로컬 어휘를 만들되 연결 근거를 남긴다.

### 결과 — 표준 셋에 걸고 나머지는 로컬 (2026-08-26)

#### Phase 13의 `v:section_of` 를 `dcterms:hasPart` 로 바꾼다

Phase 13은 「`dcterms:isPartOf`는 range가 `v:Folder`라 못 쓴다 → 새 속성을 만든다」로
끝냈다. **절반만 맞았다.**

```turtle
dcterms:isPartOf  rdfs:range v:Folder .    # 이미 있다. 쓰면 문서가 폴더가 된다
dcterms:hasPart                            # 우리 ttl 에 없다. 딸려오는 제약이 없다
```

dcterms 온톨로지 파일을 **import 하지 않는다.** 추론기가 보는 것은 우리 ttl뿐이라
`dcterms:hasPart`에는 외부 공리가 붙지 않는다. 지역 선언만 하면 된다.

```turtle
dcterms:hasPart rdfs:range v:Section .
```

그리고 이것이 **폴더를 타입하는 것과 같은 수법이다.** `isPartOf`의 range가 폴더
764개를 `v:Folder`로 타입하듯, `hasPart`의 range가 섹션을 `v:Section`으로 타입한다.
어휘가 하나 줄고 표준을 하나 더 쓴다.

**domain은 선언하지 않는다.** 폴더도 언젠가 part를 가질 수 있고, Phase 9가 domain
하나로 폴더 764개를 잘못 타입한 자리가 바로 그 옆이다.

#### 관계 8개 — 둘만 표준에 건다 (2026-08-31에 7개가 됐다)

ttl이 이미 쓰는 방식 그대로다. **우리 이름을 표준 아래에 단다.**

```turtle
v:builds_on rdfs:subPropertyOf dcterms:references .   # 지금 있는 것
```

| 우리 것 | 표준 | 근거 |
|---|---|---|
| `v:derived_from` | `prov:wasDerivedFrom` | 「A가 B에서 나왔다」와 의미가 겹친다 |
| `v:informs` | `prov:wasInfluencedBy` | PROV에서 가장 넓은 영향 관계 |
| `v:as_of` | `dcterms:date` | 「자원 생애의 한 시점」 |
| `v:contradicts` | — | 로컬 |
| `v:diverges_from` | — | 로컬 |
| `v:applies` | — | 로컬 |
| ~~`v:violates`~~ | — | **2026-08-31 삭제.** 주어가 문서가 아니다 — [`relations-v0.md`](../part3/relations-v0.md) |
| `v:expresses` | — | 로컬 |
| `v:answered_by` | — | 로컬 |

**PROV-O 전체를 들이지는 않는다.** Entity·Activity·Agent 모델은 Phase 15의
provenance 몫이고, 여기서는 속성 둘을 표준 아래 다는 것까지다.

#### 살펴보고 안 쓰기로 한 것

**CiTO** (Citation Typing Ontology)가 놀랍도록 가깝다.

```
cito:disagreesWith   ≈ contradicts
cito:extends         ≈ diverges_from
cito:citesAsEvidence ≈ derived_from
```

**안 쓴다.** CiTO는 **출판물 사이의 인용**을 위한 어휘다. `cito:disagreesWith`는
「인용하는 쪽이 인용된 쪽에 동의하지 않는다」는 **저자의 태도**고, 우리
`contradicts`는 「둘 다 참일 수 없다」는 **명제 사이의 관계**다. 가깝지만 다르다.

이 Step의 규칙이 정확히 이것을 겨냥한다 — 「이름이 비슷하다는 이유만으로 재사용하지
않는다」.

#### 클래스 셋은 로컬

```
v:Section    DoCO 의 doco:Section 이 있다.  안 쓴다 — 한 단어 때문에 온톨로지 하나를
                                            통째로 import 하게 되고, Step 4의
                                            「네트워크 없이 재현」이 깨진다
v:Insight    표준 없음
v:Question   schema:Question 이 있다.       안 쓴다 — Q&A 사이트 모델이라
                                            acceptedAnswer 를 전제한다
```

## Step 3 — 추론과 검증을 분리한다

| 요구 | 위치 |
|---|---|
| `Principle`은 `KnowledgeEntity`다 | RDFS/OWL |
| `operationalizedBy`의 역관계 | OWL 또는 질의 |
| 원칙에는 근거가 최소 하나 있어야 한다 | SHACL, Phase 16 |
| 폐기 근거에 의존하면 재검토한다 | 운영 규칙, Phase 17 |
| 승인되지 않은 제안은 확정 사실이 아니다 | 데이터셋 경계, Phase 15 |

특히 domain/range는 검증 규칙이 아니다. Phase 9에서처럼 과도한 선언이 잘못된 타입을
대량 추론할 수 있으므로 필요한 경우에만 둔다.

### 결과 — domain 을 전부 지웠다. 살아 있는 오타이핑 27개가 있었다 (2026-08-26)

#### 설계가 아니라 실물이었다

```
Content ∩ Imported     10        source-note 가 「내가 쓴 것」으로도 타입돼 있었다
Content ∩ Structural   17
                       ──
                       27
```

```
600 Content Observatory/601 Books/개발/AWS 비용 최적화 바이블/KAO 방법론.md
   type: source-note                      ← 책 필사. 저자의 말

200 Dev Knowledge Base/207 DevOps/AWS/Cost Optimization/08 FinOps 실천.md
   type: concept
   builds_on: [[KAO 방법론]]               ← 정상이다. 책을 딛고 내 노트를 썼다
```

```turtle
v:builds_on rdfs:range v:Content .    # 「builds_on 이 가리키는 것은 언제나 내 글이다」
```

```
<08 FinOps>  v:builds_on  <KAO 방법론>      데이터
v:builds_on  rdfs:range   v:Content         스키마
─────────────────────────────────────────
<KAO 방법론>  a  v:Content                   ← 거짓
```

domain 쪽으로도 샜다. `CEO Talk — 강재윤 대표.md`는 `type: source-note`인데 자기
`builds_on`을 갖고 있어 `rdfs:domain v:Content`가 그것을 내 글로 만들었다.

`v:Content`의 주석이 약속한 질의가 **「my own thinking, source-notes and
scaffolding excluded」**인데, 그 질의가 27개 틀린 채로 돌고 있었다. **에러도 경고도
없었다.** 「두 역할에 동시에 든 것이 있나」를 일부러 물어서 나왔다.

#### 전수 결산 — 선언 11개 중 2개만 살아남았다

기준은 하나. **그 문장이 참인가.**

```
dcterms:isPartOf 의 목적어는 언제나 폴더다      참      773개를 옳게 타입한다   남긴다
dcterms:subject  의 목적어는 언제나 태그다      참      245개를 옳게 타입한다   남긴다

v:builds_on 의 목적어는 언제나 내 글이다        거짓     27개를 틀리게 타입      지운다
v:links_to  의 목적어는 언제나 문서다           곧 거짓  섹션이 문서가 된다      지운다
v:hub · dcterms:replaces · created · abstract          0개를 타입한다          지운다
```

**`v:Document`를 타이핑하는 선언이 여섯인데 전부 0을 벌었다.** 문서가 문서라는 것은
`type:`이 이미 말한다. 짐작이 필요 없는데 짐작하고 있었다.

**domain 은 하나도 남지 않았다.** Phase 9가 `isPartOf`의 domain으로 폴더 764개를
Document로 만든 그 자리를 나머지 술어 전체에 한 번씩 적용한 결과다.

#### 추론을 막은 것이 아니다

```
                     지금      고친 뒤     차이
v:Document          4,021     4,021        0
v:Content           2,570     2,543      -27      ← 틀린 것만 빠진다
v:Imported          1,257     1,257        0
v:Structural          221       221        0
v:Folder              773       773        0
skos:Concept          245       245        0

전체 트리플         76,824    76,758      -66
```

살아남는 추론 — subClassOf 사슬(4,021개를 세 역할로), `isPartOf` range(폴더 773),
`subject` range(태그 245), `builds_on` 이행성, `links_to` 역관계. **빠지는 것은
「관계가 걸렸다는 사실에서 상대의 역할을 짐작하는」 규칙뿐이고, 그 짐작이 27번
틀렸다.**

#### 부정 테스트 4개 (`tests/test_inference.py`)

```
source-note 는 절대 Content 가 되지 않는다
세 역할은 서로소다                          Content ∩ Imported · ∩ Structural
추론만으로 v:Document 가 되는 자원이 없다
섹션은 v:Document 가 아니다                 ← 앞당겨 건 방어
```

**넷 다 옛 온톨로지에서 실제로 실패하는 것을 확인했다.** 공허하게 통과하는 테스트가
아니다. 네 번째는 섹션 파서가 없어 손으로 섹션을 만들어 걸었다 — **섹션이 도착하는
날이 곧 `links_to`의 range가 Phase 13을 되돌리는 날**이라 미리 잠갔다.

#### 추론·검증·운영의 자리

| 요구 | 자리 | 언제 |
|---|---|---|
| 문서 유형이 역할 아래 있다 | RDFS `subClassOf` | 있다 (Phase 8) |
| 섹션이 `v:Section` 이다 | RDFS `range` (`dcterms:hasPart`) | Phase 15 |
| 질문이 `v:Question` 이다 | RDFS `domain` (`v:answered_by`) | Phase 15 |
| 인사이트가 `v:Insight` 이다 | **파서가 적는다** (제목 접두에서) | Phase 15 |
| `contradicts` 의 반대 방향 | OWL `SymmetricProperty` | Phase 15 |
| `applies`·`informs` 의 역방향 | **질의의 `^`** — 선언하지 않는다 | — |
| 원칙에 근거가 최소 하나 | SHACL | Phase 16 |
| 600에 사견이 없다 (C16) | SHACL | Phase 16 |
| `type` 오분류 (C24) | SHACL | Phase 16 |
| 폐기 근거에 의존하면 재검토 | 운영 규칙 | Phase 17 |
| 「아직도 그렇게 믿는가」 (C08) | 운영 규칙 | Phase 17 |
| `proposed` 는 기본 질의에 안 나온다 | 데이터셋 경계 | Phase 15 |

**`v:Insight`가 추론이 아닌 것이 요점이다.** 제목이 `인사이트 N:`이면 그 섹션이
인사이트다 — 파서가 읽어서 적는 사실이지 추론기가 만들 사실이 아니다.

`derived_from`은 **이행적으로 선언하지 않는다.** PROV도 derivation을 일반적으로
이행적이라 하지 않고, Phase 9가 이미 쟀다 — OWL RL 물질화는 트리플을 2.81배로
늘리고 질적으로 새로운 유용한 사실은 0개였다.

`informs`는 **대칭이 아니다.** C09의 「상호보완적」은 양방향이 성립하는 사례이지
관계가 대칭이라는 뜻이 아니다. 둘 다 참이면 둘 다 적는다.

## Step 4 — 모듈과 버전 정책을 정한다

한 파일에 모두 넣기보다 책임별 모듈을 검토한다.

```text
ontology/
├── artifact.ttl
├── knowledge-kernel.ttl
├── profiles/
│   ├── engineering.ttl
│   └── personal-philosophy.ttl
├── provenance.ttl
└── alignments.ttl
```

실제 파일 구조는 이 Phase에서 확정한다. 다음은 반드시 결정한다.

- ontology version IRI
- 변경 로그
- deprecated term 처리
- 데이터 migration 필요 여부
- import를 네트워크 없이 재현하는 방법

### 결과 — 한 파일로 둔다 (2026-08-26)

```
현재      46 트리플 · 139줄
Step 1~3 을 반영한 뒤   89 트리플
```

**46개를 6개 파일로 쪼갤 수 없다.** 위 그림은 seam이 있을 때의 모양이고, 지금은
seam이 없다 — profile 후보였던 `engineering.ttl`에 들어갈 어휘가 **0개**다
(`v:Pattern`을 Step 1이 뺐다). 쪼개면 import 순서와 「어느 파일을 안 불렀지」라는
실패 경로만 생긴다.

**쪼갤 조건을 대신 적어둔다.** 두 번째 profile이 생기거나(다른 대역이 못 읽는
어휘를 가진 대역), 200 트리플을 넘거나, 둘 중 먼저 오는 쪽.

| 결정 항목 | 답 |
|---|---|
| version IRI | `https://tomato.vault/schema/0.1`. `owl:versionInfo "0.1"` |
| 변경 로그 | `docs/phases/`가 이미 갖고 있다. ttl은 그리로 가리킨다 |
| deprecated term | **문서 클래스는 삭제한다** (Phase 13 — `equivalentClass`가 OWL RL에서 모호함을 되살린다). 데이터를 가진 지식 개체 어휘가 생기면 그때 `owl:deprecated` + `dcterms:isReplacedBy` |
| 데이터 migration | **없다.** 의미 사실 0개 (Phase 13 Step 3 실측) |
| 네트워크 없는 재현 | 아래 |

#### `owl:imports` 를 쓰지 않는다 — 이미 그랬고, 앞으로도

```
현재 owl:imports    0건
```

`dcterms` · `skos` · `foaf` · `prov`는 **접두로만** 등장하고 그 온톨로지 파일은
한 번도 끌어오지 않는다. 그래서 추론기가 보는 것은 이 파일 하나뿐이고, 매 실행이
오프라인에서 재현되며, 재사용한 표준 용어는 **여기 적은 지역 제약만** 갖는다.

**Step 2가 `dcterms:hasPart`를 안심하고 쓸 수 있었던 이유가 이것이다.** 그리고 이것이
`doco:Section`을 안 쓴 이유이기도 하다 — 한 단어 때문에 온톨로지 하나를 통째로
들이면 이 성질이 깨진다.

## Step 5 — 논리 일관성과 질문 적합성을 테스트한다

- Turtle 파싱 테스트
- 기대한 subclass·inverse·subproperty 테스트
- 의도하지 않은 유형 추론 테스트
- 모순 사례 테스트
- 각 역량 질문에 필요한 graph pattern 작성
- 전체 ontology closure 크기와 시간 측정

### 결과 — 255개 통과 (2026-08-26)

| 요구 | 자리 |
|---|---|
| Turtle 파싱 | `test_ontology.py` — 있었다 |
| subclass·inverse·subproperty | `test_ontology.py`·`test_inference.py` — 있었다 |
| 의도하지 않은 유형 추론 | `test_inference.py` 부정 테스트 **4개 신규** |
| 모순 사례 | 세 역할이 서로소 (같은 파일) |
| 역량 질문 graph pattern | `test_competency.py` **신규 10개** |
| closure 크기·시간 | 아래 |

```
RDFS     27,463 → 52,543   1.91배    2.5초
OWL RL   27,463 → 77,035   2.81배   15.0초
```

Phase 9의 판정이 그대로다 — **OWL RL은 2.81배로 부풀리고 질적으로 새로운 유용한
사실은 만들지 않는다.** 새 어휘 39 트리플이 늘어난 것이 전부다.

#### 질문 적합성 — 온톨로지 질문 셋에 그래프 패턴을 붙였다

`tests/test_competency.py`. 사실은 손으로 적었다 — 파서가 Phase 15라 fixture가
유일한 ABox이고, **fixture에서 답 못 하는 어휘는 vault에서도 답 못 한다.**

```sparql
# C02 — 결정의 근거 tradeoff·출처와 그 출처의 현재 상태
SELECT ?target ?kind ?status WHERE {
  ?decision v:derived_from ?target .
  ?target a ?kind .
  OPTIONAL { ?target v:status ?status }
}
```

**이 패턴이 `derived_from`의 흡수 판단을 증명한다.** 관계 하나로 tradeoff와
source-note를 구분한다 — `?kind`가 대상의 `type`에서 오기 때문이다. 관계를 다섯으로
쪼갤 필요가 없었다는 것이 여기서 확인된다.

```sparql
# C08 — 믿음이 어떻게 바뀌었고 무엇이 바꿨나
SELECT ?later ?earlier ?when ?cause WHERE {
  ?later v:diverges_from ?earlier ; v:as_of ?when .
  OPTIONAL { ?later v:derived_from ?cause }
}
```

**섹션 단위 없이는 아예 표현이 안 되는 질문이다.** 한 문서에 24개 믿음이 각자 날짜를
갖고 있다.

```sparql
# C27 — 이 하위 질문은 어느 대역에서 답을 얻나, 그리고 못 얻는 것은
SELECT ?question ?answer WHERE {
  ?question a v:Question .
  OPTIONAL { ?question v:answered_by ?answer }
}
```

**`OPTIONAL`이 이 질문의 알맹이다.** inner join이면 답 없는 질문이 사라지는데,
그게 흥미로운 절반이다. Phase 7의 `summaries()`가 쓴 수법과 같다.

#### 공허한 통과를 두 번 잡았다

부정 테스트를 옛 온톨로지에 대고 돌려 **넷 다 실제로 실패하는 것**을 확인했다.

```
Content ∩ Structural   fixture 가 허브를 builds_on 대상으로 안 갖고 있었다  → 고쳤다
섹션은 Document 가 아니다  섹션 파서가 없어 손으로 섹션 IRI 를 만들어 걸었다
```

추론에 기대는 두 단언도 선언을 빼고 돌려 확인했다.

```
v:answered_by rdfs:domain v:Question   있음 → 질문으로 타입됨 · 없음 → 안 됨
dcterms:hasPart rdfs:range v:Section   있음 → 섹션으로 타입됨 · 없음 → 안 됨
```

## 산출물

- 핵심 온톨로지 0.1 — `vault-ontology.ttl` (46 → 89 트리플)
- 어휘별 competency mapping — 모든 `rdfs:comment`가 자기 질문 번호를 이름으로 댄다
- 재사용 표준과 로컬 어휘 결정 기록 — Step 2
- ontology version·deprecation·migration 정책 — Step 4
- 논리 회귀 테스트 — `test_inference.py` 부정 4개 · `test_competency.py` 10개

## 완료 조건

- [x] 클래스 8~12개, 핵심 관계 10~15개 이내에서 시작한다.
      **클래스 3개 신규**(`v:Section`·`v:Insight`·`v:Question`) + 기존 문서 17개,
      **관계 8개**(2026-08-31에 `violates`를 빼서 **7개**) + 상태 4개.
      상한은 목표가 아니다 (관측 7).
- [x] 모든 어휘가 실제 역량 질문에 연결된다.
      후보 13개 중 11개를 이 규칙으로 삭제했다. **`패턴` 135항목은 요구하는 질문이
      없어 넣지 않고 기록된 공백으로 남겼다.**
- [x] 문서 역할 클래스와 지식 개체 클래스가 섞이지 않는다.
      문서는 `*Document` 접미(Phase 13), 지식 개체는 접미 없음. `v:Section`은
      `v:Document`가 **아니고**, 그것을 부정 테스트가 잠근다.
- [x] 기술 주장과 믿음·가치·해석의 인식적 지위가 섞이지 않는다.
      `v:Insight`만 있고 기술 주장 클래스는 없다. `Claim`을 뺀 근거가 이것이다 —
      vault의 기술 주장은 `패턴`으로 적히고, 그것은 별도 클래스를 안 받았다.
- [x] 공통 kernel이 특정 Vault 대역의 분류 체계를 강요하지 않는다.
      profile 파일이 없다. 넣을 어휘가 0개였다 (Step 4).
- [x] 검증·운영 상태를 OWL로 억지 표현하지 않는다.
      SHACL(Phase 16)·운영 규칙(Phase 17)·데이터셋 경계(Phase 15)로 갈랐다 (Step 3 표).
- [x] 의도하지 않은 domain/range 유형 추론이 없다.
      **선언 11개를 지웠다. domain은 하나도 남지 않았다.** 살아 있던 오타이핑
      27개가 사라졌고, 새로 둔 것은 근거를 댄 둘뿐이다
      (`hasPart` range · `answered_by` domain).
- [x] Phase 1~9 회귀 테스트가 통과한다. — **255 passed**

**Phase 15로 넘긴 것** — 섹션·항목 파서가 `v:Section`·`v:Insight`를 실제로 적는
일. TBox는 여기서 끝났고 ABox가 비어 있다 (세 클래스 인스턴스 0개).

## 난이도와 위험

> **선행 관측 — [`part3-decisions.md`](../part3/decisions.md)의 관측 5~8**
>
> - **후보 목록이 vault와 어긋난다.** `Claim`은 vault에 대응물이 없고,
>   `tradeoff` 44개는 후보에 없는데 `decision`과 140건으로 이어져 있다.
>   **`Claim`을 넣을 근거와 `Tradeoff`를 뺄 근거를 각각 대야 한다.**
> - **무게는 클래스가 아니라 관계에 있다.** 클래스는 기존 13개 `type`을 승격하는
>   문제지만, 관계 후보 12개 중 vault에서 작동하는 것은 **0개**다
>   (`supersedes` 5건은 전부 미해결). 관계는 백지에서 만든다.
> - **어휘를 크게 만들 근거가 없다.** 역량 질문 30개 중 순수 온톨로지 판정은
>   **3개**다. 8~12개·10~15개는 상한이지 목표가 아니다.
> - **인식적 지위 분리의 선례가 대역에 있다.** 600 저자의 주장 → 400 내 결정 →
>   200 내 원칙. 새로 만드는 것이 아니라 형식화하는 것이다.
> - **메타 원칙이 문서로 있다.** `000 Index/Maintenance/디렉토리 철학/` 9개가
>   전부 `type: principle`이다. kernel 설계의 1차 자료로 먼저 읽는다.

**난이도: 높음. 코드는 작지만 모델 오류의 파급 범위가 크다.**

이 단계의 위험은 구현 버그보다 의미가 그럴듯하게 틀리는 것이다. 속성 하나를
Transitive로 선언하거나 domain을 넓게 잡으면 수천 개의 사실이 조용히 바뀔 수 있다.
그래서 긍정 테스트뿐 아니라 "절대 추론되면 안 되는 것"을 고정하는 부정 테스트가
필수다. 특히 개인의 관점에서 나온 해석이 전역 객관 사실로 추론되지 않는 사례를
부정 테스트에 넣는다.
