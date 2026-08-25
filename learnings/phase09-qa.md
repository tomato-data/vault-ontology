# Phase 9: Q&A

> 추론. 선언한 것을 실제로 돌려 트리플을 만든다. 그리고 프로젝트 전체의 판단을 내린다.

## 추론 기초

### Q: graph 가 뭔가

rdflib 의 자료구조. 트리플(주어·술어·목적어) 여러 개를 담는 자루다.
`build_graph` 가 vault 전체를 27,525개 트리플로 이 자루에 담았다.

두 성질:
- **집합이다.** 같은 트리플을 두 번 넣어도 하나. Phase 6 에서 links_to 가
  준 이유.
- **더할 수 있다.** `graph.add(triple)` 로 넣고, 두 그래프를 합치면 트리플이
  합쳐진다.

그 자체로는 지능이 없다. 그냥 사실의 자루다.

### Q: owlrl 은 뭔가

추론기(reasoner). 하는 일 하나 — **있는 트리플에서 규칙에 따라 새 트리플을
계산해 자루에 넣는다** (물질화, materialization).

```
<CIDR>    a  v:Concept .                    데이터
v:Concept    rdfs:subClassOf  v:Content .   스키마
→ <CIDR>  a  v:Content .                    추론기가 추가
```

추론기는 `rdfs:subClassOf` 의 뜻("A⊂B 이고 x가 A면 x는 B")을 알아서 규칙을
적용한다. 이름의 뜻: **owl** = OWL 규칙을 안다, **rl** = OWL 의 규칙 기반
프로파일(계산이 끝남을 보장).

| 규칙 묶음 | 발화 |
|---|---|
| `RDFS_Semantics` | subClassOf·subPropertyOf·domain·range |
| `RDFS_OWLRL_Semantics` | 위 전부 + TransitiveProperty·inverseOf |

### Q: close 함수는 어떻게 도나

```python
def close(data, ontology, *, owl=False):
    graph = Graph()                  # 빈 자루 새로
    for t in data:     graph.add(t)  # 데이터를 붓고
    for t in ontology: graph.add(t)  # 스키마도 붓고
    sem = owlrl.RDFS_OWLRL_Semantics if owl else owlrl.RDFS_Semantics
    owlrl.DeductiveClosure(sem).expand(graph)  # 추론
    return graph                     # 부푼 자루
```

- **왜 빈 자루를 새로 만드나** — `.expand` 는 자루를 제자리에서 부풀린다.
  원본 data 에 돌리면 오염된다. Phase 8 에서 스키마·데이터를 두 파일로
  갈라둔 걸 망친다. 폭발을 재려면(Step 3) 원본이 그대로 있어야 비교된다.
- **왜 데이터와 스키마를 한 자루에** — 추론은 둘이 같은 자루에 있어야
  발화한다. `a v:Concept`(데이터)와 `subClassOf`(스키마)가 만나야 규칙이
  짝을 찾는다.
- **`.expand`** — 규칙을 더 나올 게 없을 때까지 반복 적용. Concept→Content
  →Document 연쇄가 저절로 끝까지 간다.

한 줄: graph 는 사실의 자루, owlrl 은 규칙으로 새 사실을 만드는 기계,
close 는 데이터와 스키마를 한 자루에 부어 그 기계를 돌린 결과다.

### Q: 추론된 트리플은 이미 참인데 안 적힌 걸 적는 건가

그렇다. "설명"이 아니라 "드러냄"이다. `<CIDR> a v:Content` 는 추론기가
새로 만든 지식이 아니라, 규칙과 데이터가 주어진 순간 **이미 참이었지만
문장으로 안 적힌** 사실이다. 추론기는 그걸 명시적으로 적을 뿐이다.

비유: "철수는 서울에 산다" + "서울은 한국에 있다" → "철수는 한국에 산다"
는 이미 참이다. 새로 알아낸 게 아니라 말 안 했을 뿐이다.

추론기의 세 성질:
- **결정적** — 추측·창의 없음. 규칙이 허락하는 것만.
- **단조적** — 더하기만 한다. 지우거나 고치지 않는다.
- **고정점에서 멈춤** — 더 나올 게 없을 때까지 (`.expand`).

이 "더하기만"이 Phase 9 의 큰 대목으로 이어진다. 없음(뺄셈·부정)을 표현
못 하니 "summary 없으면 위반"을 OWL 로 못 쓴다. 그게 OWA 이고, 검증은
SHACL 의 일이다.

### Q: 원본과 추론 그래프는 별개인가, 쿼리마다 부푸나

**별개다.** close 는 새 Graph 객체를 반환한다. data·ontology 원본은 그대로.
메모리에 그래프가 둘(원본, 부푼 것).

**쿼리마다 부풀지 않는다.** 부풀림은 `.expand()` 한 번에 끝난다. 그 뒤
그래프는 얼어붙은 자루다. 쿼리는 읽기만 하고, 100번 물어도 크기 불변.

이게 이 프로젝트의 핵심 교환:

| | 계산 시점 | 쿼리 비용 | 빌드 비용 |
|---|---|---|---|
| Phase 7 (`+`,`^`) | 쿼리마다 | 매번 계산 | 없음 |
| Phase 9 (물질화) | 빌드에 한 번 | 그냥 읽기 | 폭발 (Step 3) |

한 번 비싸게 부풀려 두고 그 뒤론 싸게 읽는다. 대가는 그 "한 번"이 몇 배로
터지는가. (참고: forward-chaining=미리 다 만듦=owlrl / backward-chaining=
물을 때마다 거꾸로 따짐. 우리는 앞쪽.)

## Step 3 — 폭발 측정 (실제 vault)

추론 전 data 27,529 + ontology 58 = 27,587.

| 추론 | 트리플 | 증가 | 배수 | 시간 |
|---|---|---|---|---|
| RDFS only | 53,302 | +25,715 | x1.93 | 3.0s |
| RDFS + OWL RL | 77,478 | +49,891 | x2.81 | 16.6s |

거의 3배, 16.6초. SQLite 빌드 ~1초 · 쿼리 <1ms 와 비교하면 큰 비용이다.

### 무엇이 늘었나 (OWL RL 기준)

| 술어 | 전 → 후 |
|---|---|
| `rdf:type` | 3,996 → 28,928 (**+24,932**) |
| `builds_on` | 415 → 718 (+303, 이행 폐쇄) |
| `linked_by` | 0 → 8,292 (역링크 전량 물질화) |
| `links_to` | 8,292 → 8,292 (불변) |

`rdf:type` 폭발의 절반은 **잡음**이다.

```
rdfs:Resource  7,328     ← 모든 노드에 붙는다
owl:Thing      7,328     ← 모든 노드에 붙는다
v:Document     4,761
v:Content      2,545
...
```

`rdfs:Resource` + `owl:Thing` = 14,656. 노드마다 "이것은 자원이다 / 사물이다"
를 박는다. 참이지만 **어떤 질의도 벌지 못하는** 트리플이다. 폭발의 상당량이
질의력 없는 잡음이라는 게 실측으로 나왔다.

## Step 4 — domain/range 가 만든 이상한 것 (핵심 발견)

**폴더 764개가 v:Document 로 추론됐다.** 문서는 3,995개인데 v:Document 는
4,761개 — 차이 764가 폴더다.

원인은 내가 Phase 8 에서 넣은 축입이다.

```turtle
dcterms:isPartOf rdfs:domain v:Document .
```

그런데 isPartOf 의 주어는 문서만이 아니다. **폴더도 상위 폴더의 isPartOf
주어**다 (`folder isPartOf parentFolder`). domain 규칙이 발화해서 "isPartOf 의
주어는 Document 다 → 이 폴더는 Document 다"를 만들어버린다.

이게 Phase 8 이 경고한 함정의 실물이다 — **domain/range 는 검증이 아니라
추론이다.** 잘못된 데이터가 아니라 **너무 넓은 스키마 축입**이 764개의 헛
사실을 낳았다. lint(닫힌 세계)라면 "폴더는 Document 가 아니다"라고 거부했을
텐데, OWL(열린 세계)은 "그렇다면 폴더도 Document 인 것이다"라고 만들어낸다.

**교훈: 재사용한 표준 속성에 로컬 domain 을 거는 건 위험하다.** isPartOf 는
문서·폴더가 공유하는데, 한쪽 타입으로 domain 을 좁히면 다른 쪽이 오염된다.

## OWA/CWA — 실물로 확인

"필수 필드"를 OWL 로 표현하려다 실패해봤다.

- Content 노트 하나에 summary(dcterms:abstract) 를 안 붙인다.
- OWL 로 "모든 Content 는 abstract 를 최소 1개 가진다"(owl:minCardinality 1
  Restriction)를 선언한다.
- OWL RL 추론기를 돌린다.

결과: **위반 0건.** owl:Nothing(모순) 트리플 0개. 없던 abstract 를 만들지도
않았다. 추론기는 "이 노트는 잘못됐다"를 **말하지 못한다.**

이유: OWL 은 열린 세계(OWA)다 — 안 적힌 건 거짓이 아니라 모를 뿐. 추론기는
더하기만 하니(단조적) "없으면 위반"이라는 뺄셈을 표현할 방법이 없다. Phase 4
lint(닫힌 세계, 안 적히면 거짓)라면 즉시 위반이었을 것을.

**결론: 검증은 OWL 이 아니라 SHACL 의 일이다.** Phase 4 의 lint 가 실은 SHACL
이 하는 일이었다. OWL=추론, SHACL=검증. 이 프로젝트는 차이를 이해하는 게
목표였고, 여기서 몸으로 확인했다.
