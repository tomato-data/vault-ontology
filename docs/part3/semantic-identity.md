# 의미 정체성 계약 — Phase 13 정본

> Phase 13 Step 1~5의 결정만 모았다. 왜 그렇게 정했는지는
> [`phase13.md`](../phases/phase13.md)에 근거와 실측이 함께 있다.
> **Phase 15는 이 문서를 보고 구현한다.**

---

## 1 · 클래스 이름

문서 유형 13종은 전부 `Document` 접미를 갖는다. 접미 없는 이름은 쓰지 않는다.

```
concept   → v:ConceptDocument      log         → v:LogDocument
procedure → v:ProcedureDocument    reflection  → v:ReflectionDocument
reference → v:ReferenceDocument    project-doc → v:ProjectDocument    ← 예외
principle → v:PrincipleDocument    tradeoff    → v:TradeoffDocument
decision  → v:DecisionDocument     source-note → v:SourceNoteDocument
case      → v:CaseDocument         hub         → v:HubDocument
                                   review      → v:ReviewDocument
```

`project-doc`만 예외다. 기계적으로 붙이면 `ProjectDocDocument`로 말을 더듬는다.
`vault/rdf.py`의 `_class_name`에 주석과 함께 들어 있다.

**호환 공리를 두지 않는다.** `owl:equivalentClass v:Principle`을 두면 OWL RL 닫힘이
모든 문서를 다시 `v:Principle`로 타입해 없애려던 모호함이 되살아난다.

역할 상위 클래스는 그대로다 — `v:Document` · `v:Content` · `v:Imported` ·
`v:Structural`. 이들은 문서 유형이 아니라 역할이라 접미를 붙이지 않는다.

---

## 2 · 의미의 최소 단위

```
기본        문서                     4,185개 (98.8%)
하위 단위    제목(heading)            49개 문서 · 항목 320개
안 만든다    블록 ID · 문장 · 줄 번호
```

「최소 단위를 제목으로 바꾼다」가 아니다. **필요한 데서 제목까지 내려간다.**

하위 단위가 필요한 문서의 판별 기준 — 번호 붙은 항목 제목이 3개 이상.

```markdown
### 인사이트 1: 코드 품질 = 성능 + 유지보수성
### 패턴 2: …
### 교훈 3: …
```

접두는 `인사이트` · `패턴` · `원칙` · `교훈` · `사례` · `규칙` · `항목`이 관측됐다.
**이 목록은 현황이지 고정된 어휘가 아니다.** 새 접두가 나오면 늘린다.

---

## 3 · ID

**새 ID를 발급하지 않는다. wikilink가 ID다.**

```
문서     [[문서명]]              또는  [[경로/문서명]]
섹션     [[문서명#제목]]
```

근거 — `.vault.ttl`은 매 실행마다 통째로 재생성되므로 vault 밖에 남는 IRI가 없다.
살아남아야 하는 참조는 vault 안에 사람이 쓴 wikilink뿐이고 Obsidian이 그것을
유지한다.

### 중복 이름은 경로로 한정한다

```
이름이 겹치는 것   43개 이름 · 파일 194개 (4.6%)
   17  SKILL       16  Hub       15  Worklog       7  _Insights
```

`_Insights` 7개가 §2의 대상 문서들이다. **그 49개는 반드시 경로를 포함해서 적는다.**

```yaml
✗  derived_from: ["[[_Insights#인사이트 3]]"]
✓  derived_from: ["[[Q1. Better Developer/_Insights#인사이트 3]]"]
```

### 의미 링크의 깨짐은 본문 링크보다 강하게 잡는다

본문 링크가 깨지는 것은 감수한다. **의미 사실이 깨지는 것은 감수하지 않는다.**
`lint`에 별도 규칙으로 단다.

### 불투명 ID는 만들지 않는다

「문서는 지웠는데 지식 개체는 남긴다」는 wikilink로 못 한다. 그것이 필요해지는
때는 제안·승인 기록이 시간축을 가질 때이고 그건 보류된 Phase 19다.

---

## 4 · IRI 계약

```
문서    https://tomato.vault/doc/{경로}                    .md 를 뗀다
섹션    https://tomato.vault/doc/{경로}#{제목}              ← 새로 만든다
폴더    https://tomato.vault/folder/{경로}
태그    https://tomato.vault/tag/{태그}
어휘    https://tomato.vault/schema/
```

지식 개체 공간은 만들지 않는다. **이 vault에는 문서 없이 떠다니는 지식 개체가
사실상 없다** — 3개 이상 문서가 가리키는 미작성 대상이 34개뿐이고 대부분 TRPG
미작성분이거나 `.md`가 아닌 스킬 디렉터리다.

### 이스케이프

`ESCAPES`는 `#`을 `%23`으로 바꾼다. **구분자 `#` 하나만 이스케이프에서 빼고,
제목 안의 문자는 그대로 이스케이프한다.**

```
<https://tomato.vault/doc/500%20Mind%20Compiler/Q1.%20Better%20Developer/_Insights#인사이트%203:%20TDD%20자동화%20=%20학습%20효율>
                                                                                  ↑ 이 하나만 날것
```

### 섹션 앵커 해석 규칙

IRI에 들어가는 것은 **문서에 실제로 적힌 제목 전체**다. 링크는 둘 다 닿는다.

```
[[doc#인사이트 3]]                          → 첫 `:` 앞부분과 정확 일치
[[doc#인사이트 3: TDD 자동화 = 학습 효율]]     → 제목 전체와 정확 일치
```

**앞부분 일치(prefix)로 구현하면 안 된다.** `인사이트 1`이 `인사이트 10`에도
걸린다. 첫 `:` 앞부분과의 **정확 일치**여야 `인사이트 1 ≠ 인사이트 10`이 성립한다.

### 섹션이 어느 문서 것인지 — `dcterms:hasPart` 를 쓴다

**`dcterms:isPartOf` 를 쓰면 안 된다.**

```turtle
dcterms:isPartOf rdfs:range v:Folder .     # 이미 선언돼 있다
```

`<섹션> dcterms:isPartOf <문서>`를 쓰면 추론기가 `<문서> a v:Folder`를 만든다.
Phase 9가 폴더 764개를 Document로 잘못 타입했던 것과 같은 사고다 (그때는 domain,
이번엔 range).

**대신 방향을 뒤집어 `dcterms:hasPart` 를 쓴다.** dcterms 온톨로지를 import 하지
않으므로 이 술어에는 외부 공리가 붙지 않는다. 지역 선언만 하면 된다.

```turtle
dcterms:hasPart rdfs:range v:Section .     # domain 은 선언하지 않는다

<문서> dcterms:hasPart <문서#제목> .
```

range가 섹션을 `v:Section`으로 자동 타입한다 — `isPartOf`의 range가 폴더를 타입하는
것과 같은 수법이다. **domain을 선언하지 않는 이유**: 폴더도 언젠가 part를 가질 수
있고, Phase 9가 domain 하나로 폴더 764개를 잘못 타입한 자리가 바로 그 옆이다.

> Phase 13은 여기서 새 속성 `v:section_of`를 만들기로 했다가, Phase 14 Step 2
> (표준 어휘 재사용 범위)에서 뒤집었다. **표준으로 되는 일에 로컬 어휘를 만들지
> 않는다.**

---

## Phase 15가 할 일

```
links.py:18      # 에서 자르는 대신 (문서, 제목) 으로 나눈다
rdf.py           section_iri · v:Section · dcterms:hasPart
vault-ontology.ttl  두 어휘 선언
tests            rename · move · split · merge 시나리오 (섹션 단위)
```

`[[문서#제목]]` 67건이 지금은 문서로 뭉개진다. 분리하면 `links_to` 총계가 움직인다.
**회귀가 아니라 정정이고, 숫자가 바뀐 이유로 기록해 둔다.**
