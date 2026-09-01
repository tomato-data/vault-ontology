# Phase 15 — 의미 사실 그래프 빌더

> 승인된 의미 입력을 재현 가능한 ABox와 provenance로 변환한다.

## 목표

Phase 12의 작성 계약을 읽어 다음 세 층을 분리한 데이터셋을 만든다.

```text
asserted graph    사람이 승인한 사실
proposed graph    미승인 제안
inferred graph    다시 계산 가능한 파생 사실
```

Markdown은 계속 정본이며 그래프는 전부 다시 만들 수 있어야 한다.

## Step 1 — 입력 파서를 테스트로 고정한다

- 문서·섹션·block ID 파싱
- knowledge entity ID 해석
- 관계 대상 해석
- 근거 위치 보존
- 중복 assertion의 집합 처리
- 삭제·rename·split·merge 처리
- 잘못된 문법의 명시적 거부

현재 `build_graph`를 무리하게 확장할지 새 semantic builder를 둘지는 결합도와 회귀
위험을 측정한 뒤 결정한다. 기존 문서 그래프가 새 의미 그래프에 종속되게 만들지 않는다.

### 결합도와 회귀 위험 — 먼저 쟀다 (2026-08-31)

```
link_target 소비자      4   create · graph(SQLite) · lint · rdf
   섹션을 원하는 것       1   rdf 뿐
```

**그래서 `link_target`의 시그니처를 안 바꾼다.** 옆에 `link_parts`를 두고 옛 이름이
그것을 부른다. 나머지 셋은 「링크가 어디에 착지하는가」를 묻고, 섹션은 자기 문서에
착지하므로 답이 안 바뀐다. 결합도 비용 0.

```
블록 ID (^)             0   전 vault.  Step 1의 「block ID 파싱」은 지을 데이터가 없다
본문 # 링크            59   전부 해결됨
frontmatter # 관계      1   ← gold set의 expresses. 지금 파서가 문서로 뭉갠다
항목 문서              67 · 항목 324   (문턱을 뺀 뒤. Step 4를 볼 것)
   항목 아래 본문 링크   40
```

### 뜻밖의 숫자 — 「항목이 개별적으로 가리켜진다」는 1건이었다

`#` 링크 59건 중 **항목 문서에 닿는 것이 1건**이고, 그 1건도 앵커(`핵심 결정 4`)가
항목 제목과 안 맞는다. **항목에 해결되는 본문 링크는 0건이다.** 나머지 58건은
`[[동시성과 병렬성 기초#3. 언어별 async/await 비교]]` 같은 항해용 링크였다.

그런데 frontmatter의 유일한 섹션 참조 1건이 **gold set의 `expresses`**다.

```yaml
# 100 Private Log/.../모든 정답은 일시적이다.md
expresses:
  - "[[500 Mind Compiler/Q7. Who Am I/_Insights#인사이트 20]]"
```

**의미 사실은 항목을 가리키고, 항해 링크는 평범한 제목을 가리킨다.** 두 무리가
갈렸다.

### 결정 — 항목 제목만 섹션이 된다 (을)

세 갈래를 놓고 골랐다.

| | 항목 324 | 항목 아래 링크 40 | 평범한 제목 58 | gold `expresses` |
|---|:---:|:---:|:---:|:---:|
| 항목 + 가리켜진 제목 | 노드 | 주체가 항목 | 대상이 섹션 | ✅ |
| **항목만** ← 채택 | 노드 | 주체가 항목 | 문서로 뭉갬 | ✅ |
| 가리켜진 것만 | 60개만 | 문서에 남음 | 대상이 섹션 | ✅ |

근거 셋.

1. Phase 13이 섹션을 만든 이유는 **「500의 의미가 항목에 있다」**였고, 그건 항목이
   노드가 돼야 풀린다. 「가리켜진 것만」은 그 이유를 안 푼다.
2. 「항목 + 가리켜진 제목」이 더 얻는 58건은 **항해**다. gold set 50개를 라벨링하는
   동안 평범한 제목을 가리킨 의미 사실은 0건이었다.
3. 그 58건은 중첩 제목(`#A#B`) 규칙을 지금 정하라고 요구하는데, **그걸 요구하는
   데이터가 몇 건뿐이다.** Phase 9의 교훈 — 데이터가 없는 규칙은 「틀린 규칙이
   데이터를 기다리는 것」이다.

**넓히는 비용이 낮은 쪽을 골랐다.** `link_parts`가 `(문서, 제목)`을 이미 갈라 두므로,
「항목이냐」를 보는 조건문 하나를 지우면 382로 넓어진다. 그때 링크 58건이
이동하고 **회귀가 아니라 정정으로 한 번 기록**하면 된다.

### 접두 명단은 안 늘렸다

계약은 「새 접두가 나오면 늘린다」고 했다. 명단 밖에서 한 문서에 3회 이상 나오는
「한국어 + 번호」 제목을 전수로 훑었다.

```
차원 20문서 · 문제 15 · 예제 6 · 방법 6 · 옵션 5 · 예시 5 · 함정 4 · 원인 4 · 시나리오 4
```

**전부 문서 구조지 지식 개체가 아니다.** 「차원 1」은 분석의 축이고 「예제 3」은
예시다. 명단(인사이트·패턴·원칙·교훈·사례·규칙·항목)이 자의적이지 않다는 확인이라
그대로 뒀다.

### 파서 실측 (2026-08-31)

```
항목 문서 67 · 항목 324                      ← Step 4에서 문턱을 뺀 뒤의 값
   대역   200:28  300:22  500:12  400:3  000:2
   접두   패턴 150 · 인사이트 121 · 사례 36 · 교훈 9 · 원칙 4 · 규칙 4
항목이 주체가 되는 본문 링크        40
frontmatter 섹션 관계              해결 1 · 미해결 0
본문 # 링크 59 중 항목에 닿는 것      0        ← 전부 지금처럼 문서로 간다
```

`패턴` 150이 최다인데 이를 요구하는 역량 질문이 없다 — 온톨로지가 「의도적으로
남긴 구멍」이라 적어 둔 그 자리이고, 숫자가 그대로 확인됐다.

## Step 2 — 출처를 사실과 함께 저장한다

최소 provenance:

- 원본 artifact와 block/section
- assertion을 만든 주체
- 생성·승인 시점
- 사용한 도구 또는 모델과 버전
- asserted·proposed·inferred 상태
- 이전 assertion을 대체하거나 철회한 활동
- 주관적 진술의 관점 주체와 유효 시점
- 해석이 적용되는 프로젝트·생활·철학 맥락

PROV-O를 우선 검토하되, 질의가 지나치게 복잡해지면 로컬 profile을 정의한다.

### 8항목 판정 (2026-08-31)

Phase 14가 후보 클래스 13개 중 11개를 죽인 기준을 그대로 썼다 — **요구하는 역량
질문이 있는가, 그 데이터가 vault에 있는가.**

| | provenance 항목 | 질문 | 데이터 | 판정 |
|---|---|---|---|---|
| 1 | 원본 artifact와 block/section | **10 / 30** | 있다 | **무료** — 아래 |
| 2 | assertion을 만든 주체 | 없다 | 상수 | 안 적는다 |
| 3 | 생성·승인 시점 | 없다 | 없다 | 문서의 `created`가 대리 |
| 4 | 도구·모델과 버전 | 없다 | proposed 0건 | Phase 19 |
| 5 | asserted·proposed·inferred | 있다 | — | **Step 3** |
| 6 | 대체·철회 활동 | 없다 | 없다 | Phase 19 (보류) |
| 7 | 관점 주체와 유효 시점 | C08 | **85 / 324** | **`v:as_of` 구현** |
| 8 | 프로젝트·생활·철학 맥락 | 있다 | 있다 | **이미 그래프에 있다** |

30개 중 10개가 답의 형태에 **「근거 위치」·「원문 위치」**를 요구한다 (C04·C07·C08·
C09·C11 등). 1번은 자리값을 확실히 한다.

### 핵심 — reification을 안 한다. 주체가 곧 출처다

provenance가 비싼 이유는 **트리플에 사실을 붙이려면** reification·RDF-star·named
graph 중 하나가 필요해서다. 이 vault에서는 필요 없다.

```
<A> v:derived_from <B>      A 의 frontmatter 에 적혀 있다
<A#인사이트 3> v:links_to <C>   그 항목의 본문에 적혀 있다
<A> dcterms:hasPart <A#3>    A 의 본문에서 파생된다
```

**asserted 트리플의 출처는 언제나 그 트리플의 주체다.** 「이 사실을 어디서 읽나」의
답이 주체 IRI 안에 이미 들어 있고, Step 1이 섹션까지 내려놨으므로 **문서보다 작은
근거 위치도 공짜로 나온다.**

예외 하나 — `v:contradicts`는 symmetric이라 한쪽에만 적힌다. 반대 방향의 주체는
출처가 아니다. **그 방향은 asserted가 아니라 inferred이고, Step 3의 불변식
「inferred는 asserted에서 재생성한다」가 그것을 저장하지 않는 것으로 처리한다.**

### PROV-O — 어휘 두 개만 이미 쓰고 있고, 그걸로 끝이다

```turtle
v:derived_from  rdfs:subPropertyOf prov:wasDerivedFrom .
v:informed_by   rdfs:subPropertyOf prov:wasInfluencedBy .
```

`prov:Activity`·`prov:Agent`·`prov:qualifiedDerivation`은 **위 표의 2·3·4·6번을
표현하는 어휘**인데 넷 다 기각됐다. 남은 것을 위해 PROV-O를 import하면 어휘만
늘고 트리플은 안 는다. **로컬 profile도 따로 안 만든다 — 만들 것이 없다.**

### 8번 맥락은 이미 그래프에 있다

「해석이 적용되는 프로젝트·생활·철학 맥락」은 대역과 폴더다.

```turtle
<A> dcterms:isPartOf <folder/300 Runtime/302 BNV Solutions/…> .
```

`isPartOf`가 폴더 사슬을 끝까지 잇고 있으므로 (Phase 6, 4,758건) 맥락 질의는
지금도 된다. **새로 만들 것이 없다.**

### 7번만 코드가 됐다 — `item_date`

항목 324개 중 85개(26%)가 제목에 날짜를 단다.

```
인사이트 20: "모든 정답은 일시적이다" — 죽음관과 단기적 행복 (2026-03-22)
패턴 7: 제안-only — demote-only의 태깅판 (2026-07-14 · 자동 분류 #7)
사례 3 — 테스트 사이클 최적화 (2026-04-29 ~ 04-30): raw 측정 보존
```

**괄호 안 85건 · 괄호 밖 0건**이라 형식이 균일하다. 괄호를 요구하는 것이 규칙이고,
그래야 제목에 속한 날짜(「2026-05 회고」)가 `as_of`로 새지 않는다.

이것이 `dcterms:created`가 아니라 `v:as_of`인 이유 — 파일 날짜는 24개 인사이트가
하나를 공유하지만, **믿음이 언제 성립했는지는 항목마다 다르다.** C08이 묻는 것이
그것이다.

#### 갱신 날짜는 안 만들었다 — 11건 중 8건이 문서 꼬리말이었다

C08은 「최초 시점과 갱신 시점을 함께 적는다」를 근거로 들었고, 실제로 항목 본문에
「갱신·updated + 날짜」가 11건 잡혔다. **무엇이 그것을 걸렀나 — 그 항목이
`heads[-1]`인지 비교했더니 11건 중 10건이 마지막 항목이었다.**

```
**Last Updated**: 2026-08-31        8건   문서 꼬리말이 마지막 항목 아래 떨어진 것
> **2026-06-09 갱신 (…)**: …        3건   진짜.  날짜가 앞, 한국어
```

**규칙을 만들었으면 8건이 엉뚱한 항목에 갱신일을 달았다.** 남는 진짜가 3건이라
규칙을 안 쓴다. 이 셋은 접두 명단처럼 개수가 늘면 다시 본다.

## Step 3 — 그래프 경계를 구현한다

rdflib `Graph` 하나에 상태를 섞지 않는다. `Dataset`/named graph, 별도 산출물, 상태
predicate 가운데 실제 질의와 저장 형식에 맞는 방식을 실험한다.

필수 불변식:

- proposed 사실은 기본 질의에 나타나지 않는다.
- inferred graph는 asserted graph에서 재생성할 수 있다.
- assertion 철회가 원본 근거를 삭제하지 않는다.
- 같은 빌드를 두 번 실행해도 결과가 같다.
- 한 관점의 `Belief`가 무맥락한 전역 `Claim`으로 승격되지 않는다.

### 계약이 이미 절반을 정해 놨다 (2026-08-31)

[`semantic-authoring.md`](../part3/semantic-authoring.md) §2가 자리를 정해 뒀다.

| 상태 | 자리 |
|---|---|
| `asserted` | frontmatter **최상위** |
| `proposed` | frontmatter의 **`proposed:` 블록** (한 단계 안) |
| `rejected` | **sidecar에만.** 문서의 사실이 아니라 작업 이력이다 |
| `inferred` | **안 적는다.** 질의 시점에 계산한다 |

**`inferred`를 저장 안 한다는 결정이 이 Step의 절반을 없앤다.** 근거는 Phase 9
실측 — OWL RL 물질화가 트리플을 2.81배로 늘렸는데 질적으로 새 사실은 0개였고,
물질화하면 입력이 철회돼도 낡은 결과가 남는다.

**승인은 한 줄을 열 0으로 옮기는 것이다.** 들여쓰기가 장식이 아니라 상태 그 자체다.

### 세 후보의 비용

| 후보 | 비용 |
|---|---|
| named graph (`Dataset`·TriG) | **SPARQL 질의 8개 전부에 `GRAPH` 절**. `test_sparql.py`·`test_competency.py`도 함께 |
| 상태 predicate | **reification이 필요하다** — Step 2가 「주체가 곧 출처」로 기각한 그것 |
| **별도 산출물** ← 채택 | **0.** `.vault.ttl`은 지금 그대로 asserted 전용 |

`inferred`가 저장되지 않으므로 한 파일에 상태가 섞일 일이 없고, `proposed`는
**읽지 않는 것**만으로 분리된다. named graph는 섞인 것을 나누는 도구인데 **섞이지
않는다.**

### 경계가 실제로 지켜지는 자리

```python
# fm_list
m = re.search(rf"^{re.escape(key)}:[ \t]*\n(...)", fm, re.M)
#             ↑ 열 0 에 고정된다
```

`re.M`에서 `^`는 줄 머리에 붙지만 **들여쓰기를 허용하지 않는다.** 그래서 빌더는
`proposed:` 안쪽을 볼 수단 자체가 없다. **검사로 막는 게 아니라 구조로 못 닿는다.**

문제는 이것이 **부수 효과**라는 점이다. 누군가 「들여쓴 리스트도 읽게」 정규식을
느슨하게 하면 **vault의 모든 제안이 조용히 승인된다.** 그래서 세 개를 말로 적어
잠갔다.

```python
test_a_proposed_relation_does_not_read_as_asserted
test_a_relation_that_exists_only_as_a_proposal_reads_as_absent
test_the_proposed_block_is_not_itself_a_list
```

읽어야 할 때는 `fm_block`으로 **일부러** 읽는다. 블록을 dedent해서 `fm_list`에
그대로 넘기므로 항목을 벗기는 방식이 asserted와 같다 — 파서를 둘로 만들면 보조를
맞춰야 할 동작이 둘이 된다.

### 다섯 불변식

| 불변식 | 어떻게 지켜지나 |
|---|---|
| proposed가 기본 질의에 안 나온다 | `fm_list`의 `^`. 테스트 3개로 잠갔다 |
| inferred를 asserted에서 재생성한다 | 저장을 안 한다. `close()`는 새 그래프를 돌려주고 입력을 안 건드린다 |
| 철회가 원본 근거를 안 지운다 | 근거는 markdown이고 그래프는 파생물. 철회는 frontmatter 한 줄을 지우는 것이고 본문은 그대로다 |
| 같은 빌드를 두 번 해도 같다 | **실측했다** (아래) |
| `Belief`가 전역 `Claim`으로 안 올라간다 | **`v:Claim`이 없다.** Phase 14가 기각했다 — 이 vault의 기술적 주장은 `패턴 N:`으로 쓰인다. 올라갈 자리가 없다 |

### 실측 (2026-08-31)

```
빌드 두 번 → .vault.ttl 바이트 동일         결정론 확인. 1.7초
asserted 관계 517   builds_on 433 · derived_from 69 · supersedes 6
                    informed_by 4 · applies 2 · expresses 1 · contradicts 1 · diverges_from 1
proposed 블록을 가진 문서 0 · 관계 0
```

**proposed가 0인데 왜 지금 만드나** — 파일럿에서 라벨 48개 중 **37개(77%)가
proposed**로 소급 분류됐다. 전수 연결이 시작되면 제안이 asserted보다 많아지고,
**그때 경계를 만들면 이미 섞인 뒤다.**

## Step 4 — 증분보다 정확성을 먼저 검증한다

초기 구현은 전체 재빌드로 시작한다. 50개 기준 집합과 전체 Vault 일부를 실측한 뒤
병목이 확인될 때만 증분 갱신을 검토한다.

### 재빌드 실측 (2026-08-31 · 문서 4,051개)

```
scan_vault              0.23s
본문 읽기                0.54s
섹션 파서 (Step 1·2)     0.22s
fm_block  (Step 3)      0.01s
build_graph (RDF)       1.05s   트리플 27,700
build (SQLite)          0.89s   행 19,580
```

Step 1~3이 더한 것은 **0.23초**다. 섹션이 그래프에 들어가면 `dcterms:hasPart` 324개와
`v:as_of` 85개, 합쳐 **트리플의 1.5%**가 는다.

### 증분을 안 한다

**전체 재빌드가 1.3초다.** 증분이 사줄 것이 없고, 사려는 것보다 잃는 것이 크다.

```
증분이 필요로 하는 것        변경 감지 · 부분 무효화 · 그 둘이 맞다는 보장
증분이 못 지키는 것          「삭제된 문서의 낡은 엣지가 안 남는다」
```

Phase 9가 추론 물질화에 대해 한 말이 그대로 적용된다 — **파생물을 갱신하면 입력이
철회돼도 낡은 결과가 남는다.** 이 저장소는 처음부터 그 반대편에 서 있었다
(`build_graph`는 매번 새로 만들고, SQLite는 `DROP` 뒤에 `CREATE`한다).

**언제 다시 볼 것인가** — 문서당 0.32ms이므로 10초를 넘으려면 문서가 **31,000개**,
지금의 7.7배가 돼야 한다.

### 정확성을 테스트로 고정했다

```python
test_building_twice_yields_the_same_graph          # 결정론
test_the_same_build_serialises_to_the_same_bytes   # 산출물까지 동일
test_a_deleted_note_leaves_no_stale_edge           # ★ 증분을 안 하는 이유
test_a_renamed_note_carries_its_links              # rename
test_the_graph_can_be_thrown_away_and_remade       # 완료 조건 「지우고 복원」
```

세 번째가 논거다. `CIDR`가 `Network`를 가리키는 상태에서 `Network.md`를 지우면
**해결된 엣지가 `links_to_raw` 문자열로 돌아가야 한다.** 증분 갱신은 바로 여기를
놓친다.

전체 vault에서도 확인했다 — 빌드 두 번, `.vault.ttl` **바이트 동일**.

### 실측이 뒤집은 것 — 항목 문턱을 없앴다

Step 1은 「번호 붙은 항목 제목이 **3개 이상**인 문서에서만 항목이 노드가 된다」로
만들었다. 그 3이 어디서 왔는지 확인했더니 **규칙이 아니라 개체수 필터**였다.
`phase13.md`는 「이 vault에 문서보다 작은 단위가 필요한가」를 재고 있었고
「49개 문서 320항목」이 그 답이었다. **왜 3인지는 어디에도 없다.**

문턱을 1·2·3·4로 놓고 재봤다.

```
문턱 1:  문서 67  항목 324
문턱 2:  문서 56  항목 313
문턱 3:  문서 46  항목 292      ← 있던 값
문턱 4:  문서 30  항목 244
```

**문턱은 항목을 거의 안 줄이고 문서를 잘랐다.** 3→1이 항목을 11% 늘릴 뿐이다.
그런데 그 11%가 무엇이었냐면,

```
사례 20 → 36     principle 10개의 「사례 N — 사건 (2026-04-29)」
```

**C04(「이 원칙은 어떤 사건에 근거하는가」)가 찾던 근거다.** C04 판정은 「원칙 94개
중 사례로 이어진 것이 1개」였고 결론이 「근거가 없는 게 아니라 근거가 링크가
아니다」였다. 그 근거는 원칙 문서 안에 **날짜까지 붙은 항목 제목으로** 있었고,
문턱이 그것을 가리고 있었다.

그리고 문턱은 취약성을 만들었다.

```
항목 3개짜리 문서 16개   →  한 줄 지우면 형제 둘까지 섹션이 사라진다
항목 5개 이하 35 / 46    →  반으로 쪼개면 양쪽 다 무너진다 (항목 129개)
```

**낮춰도 안전한 이유를 실측했다.**

```
한 문서에 같은 항목 제목이 두 번          0건    → IRI 충돌 없음
문턱 3의 292가 문턱 1의 324의 부분집합    True   → 기존 섹션 주소가 하나도 안 움직인다
```

순수한 추가라 회귀가 아니다. `CARRIER_THRESHOLD`와 접두를 세던 코드가 함께
사라졌고, `item_headings`는 세 줄이 됐다.

계약 문서 [`semantic-identity.md`](../part3/semantic-identity.md) §2도 함께 고쳤다.

## Step 5 — 기존 그래프와 연결한다

- artifact IRI에서 기존 `doc_iri`로 왕복한다.
- 기존 type·tag·folder·wikilink 사실을 중복 생성하지 않는다.
- 기존 SQLite 질의와 RDF 산출물 결과를 보존한다.
- 의미 그래프가 없어도 기존 CLI가 정상 동작한다.

### 섹션이 그래프에 들어왔다 (2026-08-31)

```
27,700  →  28,302   (+602)

추가   hasPart 324 · type 177 · as_of 85 · links_to 40
제거   links_to 24
```

`type` 177은 **`v:Insight` 121 + `v:Question` 56**이다.

#### `v:Section`은 손으로 안 붙인다. `v:Insight`는 붙인다

```turtle
<문서> dcterms:hasPart <문서#인사이트 1> .     # range 가 v:Section 으로 타입한다
<문서#인사이트 1> a v:Insight .               # 이건 추론이 못 만든다
```

폴더가 `dcterms:isPartOf`의 range로 `v:Folder`가 되는 것과 같은 수법이다. 반면
`v:Insight`는 **제목 접두 말고는 아무것도 함의하지 않으므로** 파서가 쓴다 — 온톨로지
주석이 「a parser writes this, it is never inferred」라고 적어 둔 그대로다.

`패턴` 150개에는 클래스가 없다. Phase 14가 「역량 질문이 없다」로 남긴 구멍이고,
그것들은 클래스 없는 섹션으로 남는다.

#### `v:Question`은 경로에서 나온다

```
500 …/By Subquestion/…   56개   type: reflection 그대로 두고
                                빌더가 a v:Question 을 더한다
```

vault 쪽 2026-08-31 정합화의 결정이다 — **파생 가능한 사실은 frontmatter에 두 번
안 적는다.** 문서 클래스(`v:ReflectionDocument`)와 함께 붙으므로 둘 다 참이다.

#### `links_to` +40 / −24 — 회귀가 아니라 정정

항목 아래에 적힌 링크 40건의 **주체가 문서에서 항목으로 내려갔다.** 제거가 24건뿐인
이유는 **그래프가 집합**이라서다. 같은 문서가 같은 대상을 항목 밖에서도 가리키면
문서 트리플이 그대로 살아남는다 (Phase 6이 잰 「중복 1,162건이 하나로 합쳐진다」와
같은 성질).

#### 잡은 회귀 — 제목 줄의 링크 13건

`iter_links_by_item`이 제목 줄을 `continue`로 건너뛰어서, **제목 안에 쓴 링크가
그래프에서 사라졌다.**

```markdown
### 규칙 1 — 수치는 [[SSOT — 검증된 단일 출처]]에서만 가져온다
## 대부분 [[class]]에서 배운 내용과 같으므로 스킵
```

**무엇이 잡았나** — 재빌드 diff에서 `links_to_raw`가 **대체 없이 1건 줄어든 것**.
추가된 술어 목록에 `links_to_raw`가 없었다. 확인해 보니 13개 문서가 제목에 링크를
쓴다.

고친 방식은 「제목 줄도 읽되, **항목 문맥을 갱신한 다음에** 읽는다」다. 그러면
항목 자신의 제목에 있는 링크는 그 항목 것이 되고, 평범한 제목의 링크는 항목을
닫은 뒤 문서 것이 된다.

그리고 잡은 방법을 테스트로 박았다 — `iter_links`와 **링크 총수가 같아야 한다.**

```python
test_the_item_walk_finds_exactly_what_the_plain_walk_finds
```

#### 불변식 하나가 바뀌었다

「모든 트리플의 주체는 그 문서다」가 이제 거짓이다. 대신 이것이다.

```python
test_a_subject_is_the_document_or_one_of_its_own_sections
```

**주체는 문서이거나 그 문서 자신의 섹션이다.** 다른 문서의 섹션이 나오면 빌더가
열지도 않은 파일에 대해 사실을 쓰고 있는 것이다.

#### 보존 확인

```
lint 394                    기준선 그대로
build · lint · q            전부 정상
빌드 두 번 → 바이트 동일       결정론 유지
섹션 IRI 324개 전부          section_path 로 (경로, 제목 전문) 왕복
테스트 300 → 318 (+18)
```

### 의미 관계 7개가 들어왔다 (2026-08-31)

```
28,302  →  28,380   (+78)

derived_from 67 (+ _raw 2) · informed_by 4 · applies 2
contradicts 1 · diverges_from 1 · expresses 1 · answered_by 0
```

`NAMED`가 `STRUCTURAL + SEMANTIC`으로 갈렸다. 앞의 둘은 한 노트가 **글로서**
다른 노트에 어떻게 서는가를 말하고, 뒤의 일곱은 **생각으로서** 어떻게 서는가를
말한다.

#### 앵커가 안 맞을 때 — 두 종류가 갈라진다

```
links_to      문서로 물러난다
일곱          _raw 로 남는다
```

계약이 그렇게 적혀 있다 — 「본문 링크가 깨지는 것은 감수한다. **의미 사실이 깨지는
것은 감수하지 않는다.**」

근거는 실측이다. `#` 링크 59건 중 58건이 평범한 제목을 가리키고 「이 부분을 읽으라」는
뜻이므로 문서가 착지점으로 맞다. 반면 **없는 항목을 가리키는 `derived_from`은 아무것도
아닌 것에 대한 주장**이고, 문서로 물러나면 그 사실이 숨는다.

`_raw`에는 앵커까지 붙여 둔다 — `"문서#없는 항목"`. lint가 **무엇이 없어졌는지가
아니라 무엇을 의도했는지**를 보고할 수 있어야 한다.

#### `derived_from: experience` 2건 — 깨진 게 아니다

```turtle
<사건문서> v:derived_from_raw "experience" .
```

vault의 규칙이 「출처가 오래됐으면 `derived_from: experience`」다. **문서가 아닌
출처**를 가리키는 의도된 값이고, 해석되지 않는 것이 정상이다.

> **미결이었고, 2026-09-01에 닫혔다 — 아래 「문서 아닌 출처」 절.** 그때 「용례
> 2건짜리 술어를 만들지 않는다」로 미뤘는데, 개수가 아니라 **오탐률**이 판정했다.

#### `headings`를 주입한다

`edge_triples(relative, text, resolve, headings)`. **앵커는 대상 문서에 대고
검사해야 하므로**, 빌더가 지금 걷고 있지 않은 파일에 대해 묻는 유일한 자리다.
`resolve`와 같은 방식으로 주입해 이 모듈이 여전히 「어떻게 찾는지」를 모르게 뒀다.

`build_graph`는 본문을 **한 번만 읽고** 항목 색인을 먼저 만든다.

### 완료 조건 — 전부 확인 (2026-08-31)

| | |
|---|---|
| 기준 데이터의 asserted graph를 정확히 재현 | **33 / 33** · `tools/measure_phase15.py` |
| 모든 의미 assertion에서 원문 근거로 돌아간다 | 주체가 곧 출처 (Step 2) · `section_path` 왕복 324/324 |
| proposed가 확정 질의에 안 섞인다 | `fm_list`의 `^` · 테스트 3개 (Step 3) |
| 빌드가 결정론적이고 멱등적 | 두 번 빌드 → 바이트 동일 |
| 기존 그래프와 Phase 1~9 테스트가 안 깨진다 | 326개 통과 · lint 394 (기준선) |
| 그래프를 지우고 Markdown에서 복원 | `isomorphic` True |

```
gold set 답안 관계 33건   재현 33 · 실패 0
   derived_from 24 · informed_by 4 · applies 2
   expresses 1 · diverges_from 1 · contradicts 1

build_graph 1.86s   트리플 28,380
```

`expresses` 1건이 **섹션에 정확히 착지한다** — vault 전체에서 유일한 섹션 참조이고,
Step 1이 그것을 찾아낸 뒤로 이 Phase가 계속 겨눠 온 과녁이다.

```turtle
<모든 정답은 일시적이다>
    v:expresses <…/_Insights#인사이트%2020:%20"모든%20정답은%20일시적이다"…> .
```

### 덧 — 템플릿 9개를 그래프에서 뺐다 (2026-08-31)

빌드마다 rdflib가 같은 경고를 아홉 번 찍고 있었다.

```
ValueError: Invalid isoformat string: '{{date:YYYY-MM-DD}}'
```

`000 Index/Templates/` 아홉 개다. **vault가 `type: template`을 지운 결과**로, 각
템플릿이 **자기가 낳을 문서의 type**을 달고 그래프에 들어와 있었다.

```
Decision Node Template.md      type: decision      ← q type decision 이 이걸 답한다
Book Template - 개발.md         type: source-note
Daily Template.md              type: log
```

`EXCLUDED_ZONES`에 넣었다. **근거는 vault가 이미 적어 둔 것**이다.

```json
// .vault-lint.json — Phase 4 부터 있었다
"skip_frontmatter_in": ["900 Archive", "000 Index/Templates"],
"_why": "000 Index/Templates 의 frontmatter 는 데이터가 아니라 자리표시자다"
```

lint가 「이 frontmatter는 데이터가 아니다」라고 이미 말하고 있었고, 그래프 제외는
**같은 말을 다른 자리에서** 하는 것이다.

```
트리플 28,380 → 28,338 (−42)     문서 9 · 나가는 링크 13 · 폴더 1
새 links_to_raw 2                401.0 Hub 가 템플릿을 가리키던 것 (문서는 skip_files 에 이미 있다)
rdflib 경고 9 → 0
lint 394                        불변 (lint 는 in_graph 를 안 쓴다)
gold set 33/33                  불변
```

#### 다른 템플릿 디렉터리는 안 건드렸다 — 판별이 다르다

전수로 훑으니 템플릿처럼 생긴 자리가 더 있는데, **frontmatter에 자리표시자를 가진
것은 `000 Index/Templates` 뿐**이다.

```
000 Index/Templates                        9   ⚠ {{date}} 있음      ← 제외함
400 Logic Forge/499 Logic Forge Templates  3     case·decision·tradeoff
200 …/299 Principles/templates             2     reference
300 …/320.4. Applications/_Template        5     project-doc
그 밖 _template · 0000-template 등          3     project-doc
```

**「frontmatter가 데이터가 아니다」는 근거가 나머지에는 안 걸린다.** 저들의 날짜와
type은 진짜다.

> **남은 미결.** `q type decision`이 아직
> `499 Logic Forge Templates/Decision Node Template.md`를 답한다. 자리표시자
> 문제는 아니고 **「템플릿이 자기가 낳을 문서의 type을 단다」**는 문제이며, 이건
> vault 쪽 정합화의 사안이다. 여기서 정하지 않는다.

## 산출물

- semantic assertion parser
- asserted·proposed·inferred graph 분리
- provenance profile
- gold graph 재현 테스트
- 전체 재빌드 명령과 측정 결과

## 완료 조건

- [ ] 기준 데이터의 asserted graph를 정확히 재현한다.
- [ ] 모든 의미 assertion에서 원문 근거로 돌아갈 수 있다.
- [ ] proposed 사실이 확정 질의에 섞이지 않는다.
- [ ] 빌드가 결정론적이고 멱등적이다.
- [ ] 기존 그래프와 Phase 1~9 테스트가 깨지지 않는다.
- [ ] 그래프 파일을 지우고 Markdown에서 전부 복원할 수 있다.

## 난이도와 위험

**난이도: 높음. 데이터 모델과 상태 모델이 동시에 들어온다.**

현재 그래프는 파일에서 단방향으로 재생성하면 끝난다. 새 그래프는 승인·철회·출처를
보존해야 해 시간축이 생긴다. 이력을 파생 데이터에만 두면 재빌드 시 사라지고, 모두
Markdown에 넣으면 작성 부담이 커진다. 이 경계를 Phase 12의 실측 없이 정하면 안 된다.

---

## 문서 아닌 출처를 1급으로 (2026-09-01)

Round 6이 미뤄 둔 `derived_from: experience`를 닫는다. **개수가 아니라 오탐률이
판정했다.**

### 무엇이 잘못돼 있었나

작성 참조표(`000 Index/Dots/의미 라벨 5일 관찰`)가 **문서 아닌 출처를 셋** 정해 뒀는데,
빌더는 **셋 다 다루지 않았다.**

```yaml
derived_from: [[문서 이름]]                      vault 안        →  해석했다
derived_from: experience                        실무. 문서 없다   →  _raw (깨진 링크와 같은 자리)
derived_from: "ext:ai-ops-skills/…/tdd"          vault 밖        →  _raw
source_unknown: true                            찾아봤고 없었다   →  아예 안 읽었다
```

### 오탐률 100%

```
의미 관계의 _raw 값 전수 (2026-09-01)   experience 16건.  그게 전부
깨진 의미 링크                          0건
```

**Phase 16이 만든 `v:SemanticLinkShouldResolve`가 16번 경고하고 16번 다 틀렸다.**
Phase 16 Step 1이 「아무것도 안 세는 shape」를 잡았는데, 이건 그 거울상 —
**전부 잘못 잡는 shape**다. 어느 쪽이든 규칙이 말하는 것과 데이터가 다르다.

그리고 `ask evidence`가 깨진 링크에 대고 **「출처가 문서가 아니라 겪은 일이다」**라고
답했다. 거짓인데 그래프가 고칠 수 없었다 — **파서가 그 차이를 그래프가 생기기 전에
버렸기 때문이다.**

### 값을 리소스로 만든다

별도 술어도, 리터럴 허용 목록도 아니다. **객체를 리소스로 올린다.**

```turtle
<원칙>  v:derived_from  v:experience .
<질문>  v:answered_by   <https://tomato.vault/external/ai-ops-skills/…/tdd> .
<원칙>  v:source_unknown  true .
```

`derived_from`이 술어로 그대로 남고, SHACL·`ask`·`genealogy`가 전부 공짜로 구분한다.
`external/`은 `doc/`와 다른 네임스페이스인데, 이것들은 여기서 아무 파일로도 안 풀리고
`doc/`를 공유하면 **`doc_path`가 있지도 않은 파일을 이름 짓는다.**

센티널은 **해석 전에** 가로챈다. 이름으로 찾으러 보내는 것이 애초에 `_raw`로 떨어진
이유다.

### 실측

```
트리플 28,436 → 28,445
   derived_from_raw  16 → 0        ← _raw 가 다시 「깨졌다」만 뜻한다
   derived_from      +17
   source_unknown    +5            ← 예약해 둔 자리가 실제로 찼다

SHACL 「해석되지 않았다」  16 → 0    오탐이 사라졌다
```

**`source_unknown` 5건은 뜻밖이었다.** 8월 31일에 0건이라 「어휘만 두고 값은 안
만든다」고 적었는데, 하루 사이 vault 쪽에서 쓰기 시작했다. 빌더가 안 읽고 있었을
뿐이다.

### `ask`의 상태가 여섯으로 갈렸다

```
answered     vault 안의 문서
lived        v:experience — 내가 한 일에서 나왔다
external     ext: — vault 밖
searched     source_unknown — 찾아봤고 없었다
broken       _raw — 적힌 이름이 아무 데도 안 닿는다.  오류다
unrecorded   아무것도 안 적혔다 — 없다는 뜻이 아니다
```

**`broken`이 새로 생긴 것이 이 작업의 값이다.** 전에는 오류가 사실인 척했다.
