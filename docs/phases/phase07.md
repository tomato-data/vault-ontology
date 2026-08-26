# Phase 7 — SPARQL

> 모듈: `vault/sparql.py` · scope: `sparql`

## 큰 그림

Phase 6이 만든 트리플에 질의한다. **Phase 5에서 SQL로 푼 질문을 하나씩 다시 푼다.** 답이 같아야 하고, 표현이 달라야 한다.

이 Phase의 산출물은 코드가 아니라 **비교표**다.

## 핵심 개념

### 1. 기본 — 그래프 패턴 매칭

SQL은 "테이블에서 행을 고른다". SPARQL은 **"그래프에서 모양을 찾는다"**.

```sparql
SELECT ?doc ?summary WHERE {
  ?doc v:type    v:Concept .
  ?doc v:summary ?summary .
}
```

세 줄을 읽는 법: **"`?doc`이라는 미지수가 있는데, 그것의 type이 Concept이고 summary가 `?summary`인 것을 전부 찾아라."** 트리플 패턴을 나열하면 공통 변수로 자동 조인된다. `JOIN ... ON`이 없다.

### 2. property path — 이 Phase의 하이라이트

Phase 5에서 이렇게 썼다.

```sql
WITH RECURSIVE chain(id, depth) AS (
  SELECT :start, 0
  UNION SELECT e.dst, chain.depth + 1
    FROM edge e JOIN chain ON e.src = chain.id
   WHERE e.kind = 'builds_on' AND chain.depth < 10
) SELECT * FROM chain ORDER BY depth;
```

SPARQL에서는 이렇다.

```sparql
SELECT ?prereq WHERE { <doc/CIDR> v:builds_on+ ?prereq }
```

**`+` 하나다.** 이행 폐쇄가 언어에 내장돼 있다.

경로 연산자 전체.

| | 뜻 |
|---|---|
| `p+` | 한 번 이상 |
| `p*` | 영 번 이상 (자기 자신 포함) |
| `p?` | 영 번 또는 한 번 |
| `^p` | **역방향** — 역링크가 공짜다 |
| `p1/p2` | 이어붙이기 |
| `p1\|p2` | 둘 중 하나 |

`^p`가 특히 크다. Phase 5의 `q near`는 링크와 역링크를 `UNION ALL`로 두 번 썼는데, 여기서는 `v:links_to|^v:links_to` 한 줄이다.

### 3. 정직하게 비교할 것

**SPARQL이 항상 짧은 건 아니다.** 집계, 정렬, 문자열 처리는 SQL이 편한 경우가 많다. 이 Phase는 SPARQL 홍보가 아니라 **어디서 갈리는지 재는 것**이다.

| 질의 | SQL | SPARQL | 판정 |
|---|---|---|---|
| `type` 분포 | `GROUP BY` | `GROUP BY` | 비슷 |
| 고아 노트 | `NOT EXISTS` | `FILTER NOT EXISTS` | 비슷 |
| **이행 폐쇄** | 재귀 CTE 6줄 | `+` 한 글자 | **SPARQL 압승** |
| **역방향 순회** | `UNION ALL` 반복 | `^` | **SPARQL 압승** |
| 상위 10개 태그 | `ORDER BY LIMIT` | 같음 | 비슷 |
| 문자열 가공 | 함수가 풍부 | 제한적 | SQL 우세 |
| 성능 | 모든 질의 0.0~0.5ms | 2~281ms | **SQLite가 10~600배 빠름** |

마지막 줄이 이 프로젝트의 미결 판단이다. 스키마 정본:

> **판단 기준은 하나다** — 재귀 CTE로 부족해서 SPARQL property path나 추론이 필요해지는가.

### 4. 성능 — 예상하지 말고 잰다

rdflib는 **순수 파이썬 인메모리 스토어**다. SQLite는 C로 짜인 인덱스 있는 디스크 스토어다. 트리플 3~4만 개 규모에서 어느 쪽이 빠른지는 재봐야 안다.

```
SQLite 빌드   약 970ms
RDF 빌드      약 1,250ms
SQLite 질의   0.0~0.5ms
rdflib 질의   2~281ms
```

실측 결과, SQLite가 모든 질의에서 10~600배 빨랐다. **v2(Rust + Oxigraph)의 근거는 성능이 아니라 학습**이라는 사전 가설을 지지한다. 자세한 결과는 [`../learnings/phase07-sparql-vs-sql.md`](../../learnings/phase07-sparql-vs-sql.md)에 있다.

---

## Step 목록

| Step | 내용 |
|---|---|
| 1 | `SELECT` · `WHERE` · `FILTER` — Phase 5의 `q type`·`q tag` 재현 |
| 2 | `OPTIONAL` — summary 없는 문서도 나오게 |
| 3 | **property path `+`** — `q path` 재현. 재귀 CTE와 결과 대조 |
| 4 | **`^` 역방향** — `q near` 재현 |
| 5 | 집계 — `q stats` 재현 |
| 6 | **비교표 작성** — 질의별 코드 길이 · 실행 시간 · 읽기 쉬움 |

---

## 완료 기준

- [x] Phase 5의 모든 질의(`path`·`near`·`orphans`·`type`·`tag`·`stats`)를 SPARQL로 재현
- [x] **결과가 SQLite와 일치**한다 (다르면 Phase 6 모델링이 틀린 것)
- [x] 질의별 비교표가 `learnings/`에 있다 — 코드 길이·시간·주관적 읽기 쉬움
- [x] 성능 실측 숫자가 있다
- [x] "property path가 실제로 필요했던 질의"가 몇 개인지 셌다
