# Phase 9: Q&A

> 추론. 선언한 것을 실제로 돌려 트리플을 만든다. 그리고 프로젝트 전체의 판단을 내린다.

## 추론 기초

### Q: 그래프란 무엇인가

rdflib에서 트리플(주어·술어·목적어)을 저장하는 자료구조다.
`build_graph`는 vault 전체를 27,525개의 트리플로 구성된 그래프로 만든다.

두 성질:
- **집합이다.** 같은 트리플을 두 번 넣어도 하나. Phase 6에서 links_to가
  줄어든 이유다.
- **더할 수 있다.** `graph.add(triple)`로 넣고, 두 그래프를 합치면 트리플이
  합쳐진다.

그래프 자체가 추론하는 것은 아니다. 명시된 사실을 저장할 뿐이다.

### Q: owlrl은 무엇인가

추론기(reasoner)다. **기존 트리플에 규칙을 적용해 새 트리플을 계산하고
그래프에 추가한다.** 이 과정을 물질화(materialization)라고 한다.

```
<CIDR>    a  v:Concept .                    데이터
v:Concept    rdfs:subClassOf  v:Content .   스키마
→ <CIDR>  a  v:Content .                    추론기가 추가
```

추론기는 `rdfs:subClassOf`의 뜻("A⊂B이고 x가 A면 x는 B")을 알아서 규칙을
적용한다. 이름에서 **owl**은 OWL 규칙을, **rl**은 계산 종료가 보장되는
OWL의 규칙 기반 프로파일을 뜻한다.

| 규칙 묶음 | 적용 범위 |
|---|---|
| `RDFS_Semantics` | subClassOf·subPropertyOf·domain·range |
| `RDFS_OWLRL_Semantics` | 위 전부 + TransitiveProperty·inverseOf |

### Q: `close` 함수는 어떻게 동작하나

```python
def close(data, ontology, *, owl=False):
    graph = Graph()                  # 새 그래프 생성
    for t in data:     graph.add(t)  # 데이터 추가
    for t in ontology: graph.add(t)  # 스키마 추가
    sem = owlrl.RDFS_OWLRL_Semantics if owl else owlrl.RDFS_Semantics
    owlrl.DeductiveClosure(sem).expand(graph)  # 추론
    return graph                     # 물질화된 그래프
```

- **왜 새 그래프를 만드나** — `.expand`는 전달받은 그래프를 직접 변경한다.
  원본 데이터에 실행하면 추론 결과가 섞인다. Phase 8에서 분리한 스키마와
  데이터도 다시 구분하기 어려워진다. 증가량을 측정하려면 원본을 보존해야 한다.
- **왜 데이터와 스키마를 한 그래프에 넣나** — 추론하려면 둘이 같은 그래프에
  있어야 한다. `a v:Concept`(데이터)와 `subClassOf`(스키마)가 만나야 규칙이
  짝을 찾는다.
- **`.expand`** — 규칙을 더 나올 게 없을 때까지 반복 적용. Concept→Content
  →Document 연쇄가 저절로 끝까지 간다.

요약하면 그래프는 사실을 저장하고, owlrl은 규칙에 따라 새 사실을 계산한다.
`close`는 데이터와 스키마를 합친 뒤 추론한 결과를 새 그래프로 반환한다.

### Q: 추론된 트리플은 이미 참인데 안 적힌 걸 적는 건가

그렇다. "설명"이 아니라 "드러냄"이다. `<CIDR> a v:Content`는 추론기가
새로 만든 지식이 아니라, 규칙과 데이터가 주어진 순간 **이미 참이었지만
문장으로 안 적힌** 사실이다. 추론기는 그걸 명시적으로 적을 뿐이다.

비유: "철수는 서울에 산다" + "서울은 한국에 있다" → "철수는 한국에 산다"
는 이미 참이다. 새로 알아낸 게 아니라 말 안 했을 뿐이다.

추론기의 세 성질:
- **결정적** — 추측·창의 없음. 규칙이 허락하는 것만.
- **단조적** — 더하기만 한다. 지우거나 고치지 않는다.
- **고정점에서 멈춤** — 더 나올 게 없을 때까지 (`.expand`).

이 "더하기만"이 Phase 9의 큰 대목으로 이어진다. 없음(뺄셈·부정)을 표현
못 하니 "summary 없으면 위반"을 OWL로 못 쓴다. 그게 OWA이고, 검증은
SHACL의 일이다.

### Q: 원본과 추론 그래프는 별개인가? 질의할 때마다 다시 물질화하나?

**별개다.** close는 새 Graph 객체를 반환한다. data·ontology 원본은 그대로.
따라서 메모리에는 원본 그래프와 물질화된 그래프가 별도로 존재한다.

**질의할 때마다 물질화하지 않는다.** `.expand()`를 한 번 실행한 뒤에는
질의가 그래프를 읽기만 하므로, 몇 번을 질의해도 트리플 수는 변하지 않는다.

이게 이 프로젝트의 핵심 교환:

| | 계산 시점 | 쿼리 비용 | 빌드 비용 |
|---|---|---|---|
| Phase 7 (`+`,`^`) | 쿼리마다 | 매번 계산 | 없음 |
| Phase 9 (물질화) | 빌드할 때 한 번 | 저장된 결과 읽기 | 트리플 수 증가 (Step 3) |

처음에 계산 비용을 지불하고 결과를 저장하면 이후 질의는 단순해진다. 관건은
그 과정에서 트리플 수와 처리 시간이 얼마나 늘어나는가다. owlrl은 전방향 추론
(forward chaining), 질의 시점에 필요한 사실을 거슬러 찾는 방식은 후방향 추론
(backward chaining)에 해당한다.

## Step 3 — 증가량 측정 (실제 vault)

추론 전 data 27,529 + ontology 58 = 27,587.

| 추론 | 트리플 | 증가 | 배수 | 시간 |
|---|---|---|---|---|
| RDFS only | 53,302 | +25,715 | x1.93 | 3.0s |
| RDFS + OWL RL | 77,478 | +49,891 | x2.81 | 16.6s |

거의 3배, 16.6초. SQLite 빌드 ~1초 · 쿼리 <1ms와 비교하면 큰 비용이다.

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
를 붙인다. 참이지만 **실제 질의에는 도움이 되지 않는** 트리플이다. 늘어난
트리플의 상당 부분이 이런 일반 타입 정보라는 사실을 확인했다.

## Step 4 — domain/range가 만든 이상한 것 (핵심 발견)

**폴더 764개가 v:Document로 추론됐다.** 문서는 3,995개인데 v:Document는
4,761개 — 차이 764가 폴더다.

원인은 Phase 8에서 추가한 선언이다.

```turtle
dcterms:isPartOf rdfs:domain v:Document .
```

그런데 isPartOf의 주어는 문서만이 아니다. **폴더도 상위 폴더의 isPartOf
주어**다 (`folder isPartOf parentFolder`). domain 규칙이 적용되어 "isPartOf의
주어는 Document다 → 이 폴더는 Document다"라는 결론을 만들어낸다.

이 결과가 Phase 8에서 경고한 함정을 보여준다. **domain/range는 검증이 아니라
추론이다.** 잘못된 데이터가 아니라 **너무 넓은 스키마 선언**이 764개의 잘못된
사실을 낳았다. lint(닫힌 세계)라면 "폴더는 Document가 아니다"라고 거부했을
텐데, OWL(열린 세계)은 "그렇다면 폴더도 Document인 것이다"라고 추론한다.

**교훈: 재사용한 표준 속성에 로컬 domain을 거는 건 위험하다.** isPartOf는
문서·폴더가 공유하는데, 한쪽 타입으로 domain을 좁히면 다른 쪽이 오염된다.

## OWA/CWA — 실제 데이터로 확인

"필수 필드"를 OWL로 표현하려다 실패해봤다.

- Content 노트 하나에 summary(dcterms:abstract) 를 안 붙인다.
- OWL로 "모든 Content는 abstract를 최소 1개 가진다"(owl:minCardinality 1
  Restriction)를 선언한다.
- OWL RL 추론기를 돌린다.

결과: **위반 0건.** owl:Nothing(모순) 트리플 0개. 없던 abstract를 만들지도
않았다. 추론기는 "이 노트는 잘못됐다"를 **말하지 못한다.**

이유: OWL은 열린 세계(OWA)다 — 안 적힌 건 거짓이 아니라 모를 뿐. 추론기는
더하기만 하니(단조적) "없으면 위반"이라는 뺄셈을 표현할 방법이 없다. Phase 4
lint(닫힌 세계, 안 적히면 거짓)라면 즉시 위반이었을 것을.

**결론: 검증은 OWL이 아니라 SHACL의 일이다.** Phase 4의 lint가 실은 SHACL
이 하는 일이었다. OWL=추론, SHACL=검증. 이 프로젝트는 차이를 이해하는 게
목표였고, 여기서 실제 결과로 확인했다.
