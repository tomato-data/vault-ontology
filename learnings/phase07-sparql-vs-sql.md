# Phase 7 비교표 — 같은 질문, 두 언어

Phase 5는 SQLite로, Phase 7은 SPARQL로 같은 여섯 질문에 답했다. 답은
같았다(두 곳은 모델 차이로 갈렸는데, 그 갈림이 소득이다). 표현과 속도는
달랐다. 이 문서가 Phase 7의 산출물이다.

실측 환경: 실제 vault 노트 3,996개 / 트리플 27,525개. 질의 시간은 워밍업 뒤
5회 최소값. rdflib 7.6, 순수 파이썬 인메모리. SQLite는 C 인메모리.

## 한 장 요약

| 질의 | SQL 코어 | SPARQL 코어 | SQLite | rdflib | 판정 |
|---|---|---|---|---|---|
| type | `WHERE type=?` 1줄 | `?doc a ?class` 1줄 | 0.5 ms | 11 ms | 문법 비슷 · SQLite 빠름 |
| tag | `substr` 접두사 2줄 | `v:tagged/skos:broader*` 1줄 | 0.3 ms | 3 ms | SPARQL 짧음 |
| **path** | **재귀 CTE 6줄** | **`v:builds_on+` 1줄** | 0.5 ms | 2 ms | **SPARQL 압승** (depth는 잃음) |
| **near** | **쿼리 2개 + 파이썬 합집합** | **`v:links_to\|^v:links_to` 1줄** | 0.0 ms | 7 ms | **SPARQL 압승** |
| orphans | `NOT IN (SELECT dst …)` | `FILTER NOT EXISTS` | 0.0 ms | 281 ms | 문법 비슷 · SQLite 압도 |
| kinds | `GROUP BY kind` | `GROUP BY ?kind` + `VALUES` | 0.0 ms | 60 ms | 문법 비슷 · SQLite 빠름 |

## 어디서 SPARQL이 이기나

이행 폐쇄와 역방향 순회, 딱 두 곳이다.

- **path** — 재귀 CTE 여섯 줄(순환 방지 `depth < :limit` 포함)이 `+` 한
  글자가 된다. 순환도 저절로 끝난다. 집합이라 종료가 공짜다.
- **near** — 링크와 역링크를 얻으려 Phase 5는 쿼리를 둘 짜고 파이썬에서
  합쳤다. `^`가 화살표를 뒤집고 `|`가 합쳐, 한 줄이 된다.

스키마 정본의 미결 판단이 이거였다.

> 판단 기준은 하나다 — 재귀 CTE로 부족해서 property path나 추론이
> 필요해지는가.

답: **부족하진 않다.** 재귀 CTE로도 같은 답이 0.5ms에 나온다. property
path는 **더 짧지, 못 하던 걸 하게 해주진** 않는다. 적어도 이 vault 규모에선.

## 어디서 안 이기나

집계(kinds)와 부재 검사(orphans)는 두 언어가 거의 같은 문법을 쓴다.
`GROUP BY`·`COUNT`·`NOT EXISTS`는 SQL의 것을 SPARQL이 빌렸다. "SPARQL이
항상 짧다"는 착각을 이 두 줄이 깬다.

## 성능 — 예상하지 말고 쟀다

**질의 전 구간에서 SQLite가 10~600배 빠르다.** 순수 파이썬 스토어가 C
인덱스 스토어를 못 이긴다. 빌드는 비슷하다(SQLite ~970ms, rdflib ~1250ms).

```
             SQLite      rdflib
build         970 ms     1250 ms
type          0.5 ms       11 ms
tag           0.3 ms        3 ms
path          0.5 ms        2 ms
near          0.0 ms        7 ms
orphans       0.0 ms      281 ms      ← FILTER NOT EXISTS가 제일 느리다
kinds         0.0 ms       60 ms
```

이게 v2 방향에 답을 준다. 스키마 정본은 "v2(Rust + Oxigraph)의 목적은
성능이 아니라 온톨로지 학습"이라 미리 적어뒀다. **실측이 그 가설을
지지한다.** rdflib를 성능 때문에 버릴 이유는 이 규모에선 없다. 버린다면
학습(추론·SHACL·SPARQL 표현력)이 이유다.

## 답이 갈린 두 곳 — 그게 소득이다

작은 fixture에선 두 엔진이 글자까지 같았다. 실제 vault에선 두 질의가
갈렸는데, 갈림의 원인이 Phase 6에서 배운 그대로다.

### kinds — 그래프는 집합, 테이블은 bag

```
SQL  (bag):  builds_on 415 · links_to 9456 · part_of 1020
RDF  (set):  builds_on 415 · links_to 8292
중복 links_to 행 1164 →  9456 − 1164 = 8292
```

SQLite edge 테이블은 같은 링크를 여러 번 담는다. RDF는 트리플 집합이라
합쳐진다. Phase 6에서 `links_to`가 10,622 → 9,359로 준 그 성질이, 이번엔
집계 숫자로 나왔다. `part_of` 1020은 SQL에만 있다 — RDF `kinds`는 링크
술어 셋만 세고, `part_of`는 폴더를 가리키니 뺐다.

### orphans — 문서를 표시하는 보편 술어가 RDF엔 없다

```
RDF orphans        718
SQL orphans(링크만) 719   ← 1건 차이
```

RDF `orphans`는 `?doc a ?class`로 **타입 있는 문서만** 센다. 타입 없이
아무도 안 가리키는 노트 1개를 놓친다. SQLite node 테이블은 모든 행을
가지지만, RDF엔 "이것은 문서다"를 모든 문서에 붙이는 술어가 없다. 타입도
summary도 다 선택적이라(open world), 열거의 기준을 하나 골라야 한다.
Phase 8에서 `rdfs:subClassOf`로 클래스 계층을 세우면 이 열거 문제가 다시
온다.

## 배운 실수 셋

경로 연산자는 짧다. 짧아서, 틀려도 조용하다.

1. **`^` 방향** — `by_tag`에서 `^skos:broader*`로 썼다가 절반만 맞았다.
   `broader`는 「구체 → 상위」라 정방향으로 올라가야 하는데 거꾸로 내려가,
   `Stack/Python`을 단 문서를 놓쳤다. 에러가 아니라 빈 결과였다. SQLite라는
   정답지가 옆에 없었으면 그럴듯해 보였을 것이다.
2. **`SELECT`는 bag** — `neighbours`에서 양방향 이웃이 두 번 잡혔다.
   `UNION`이 자동으로 하던 중복 제거를 SPARQL은 `DISTINCT`로 명시해야 한다.
3. **`UNESCAPES` 값이 정수** — `str.maketrans`가 만든 dict는 key가
   코드포인트(정수)라, 뒤집으면 값이 정수가 된다. `chr`로 문자를 되살려야
   했다. `replace() argument 2 must be str, not int`가 정확히 가리켰다.

두 언어가 같은 함정을 공유한다(bag, NULL/미바인딩). 다른 곳은 방향과
집합성이다.
