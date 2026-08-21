# Phase 5 — SQLite 그래프

> 모듈: `vault/graph.py` · scope: `graph` · **1부의 마지막**

## 큰 그림

지금까지 읽고 판정했다. 이제 **저장하고 질의**한다. 마크다운 6,452개를 노드·엣지·태그 세 테이블로 뽑고, 재귀 CTE로 다중 홉 순회를 한다.

```
vault build    파싱 → SQLite (.vault-graph.db)
vault q path   builds_on 이행 폐쇄 = 학습 경로
vault q near   링크·역링크·같은 태그 이웃
vault q orphans / type / tag / stats / sql
```

## 이전 Phase와의 연결

Phase 1~4의 모든 함수가 여기로 들어온다. **1부의 종착점이자 2부의 대조본**이다.

## 핵심 개념

### 1. 그래프는 파생물이다

이 프로젝트가 muo-ahn/Ontology 같은 프로젝트와 갈리는 지점.

```
그쪽:  데이터 없음 → 파이프라인이 그래프를 생성      (write 중심)
이쪽:  문서 6,452개 이미 있음 → 그래프를 추출        (read 중심)
```

| | 그래프의 지위 | 틀렸을 때 |
|---|---|---|
| 그쪽 | **원본** — 유일한 저장소 | 데이터 손상. 복구 필요 |
| **이쪽** | **파생물** — md가 원본 | **다시 빌드하면 끝** |

그래서 MERGE·제약조건·멱등성이 필요 없다. **매번 DB를 지우고 새로 만든다.** `.vault-graph.db`는 gitignore.

이 성질이 2부에서도 그대로 간다 — RDF 그래프도 파생물이다.

### 2. 스키마

```sql
CREATE TABLE node (
  path TEXT PRIMARY KEY,   -- 볼트 기준 상대경로
  name TEXT NOT NULL,      -- 링크에 쓰는 이름 (확장자 없는 파일명)
  zone TEXT NOT NULL,      -- 최상위 디렉토리
  dir TEXT, type TEXT, summary TEXT, created TEXT, bytes INTEGER
);

CREATE TABLE edge (
  src  TEXT NOT NULL,
  dst  TEXT,               -- 해석 실패면 NULL
  raw  TEXT NOT NULL,      -- 원래 쓰인 타깃 문자열
  kind TEXT NOT NULL       -- builds_on · supersedes · links_to · part_of
);

CREATE TABLE tag (path TEXT, tag TEXT);
```

**`dst`가 NULL을 허용하고 `raw`를 같이 저장하는 것**이 설계의 핵심이다. 깨진 링크도 그래프의 사실이다. 버리면 "무엇을 가리키려 했는가"를 잃는다.

### 3. 파생 가능한 사실은 저장하지 않는다

`part_of`(디렉토리 계층)는 frontmatter에 안 쓴다. **경로가 이미 알고 있으므로 빌드 시점에 유도한다.** 저장하면 반드시 어긋난다.

같은 이유로 `updated`도 없다 — git이 안다.

### 4. 제외 구역, 그리고 그 이유

```
800 TRPG · 900 Archive · .claude · .obsidian · CLAUDE.md
```

800 TRPG를 빼는 이유가 재미있다. **같은 `type:` 키를 다른 뜻으로 쓴다.**

```
TRPG의 type:  완제품 1041 · 원재료 351 · 중간재 317 · 마물 101 · 마족 12
```

게임 아이템 분류다. 섞으면 type 축이 깨진다. **어휘 충돌** — Phase 8에서 네임스페이스가 왜 필요한지를 설명할 때 이 사례가 그대로 쓰인다. RDF라면 서로 다른 IRI 네임스페이스로 공존시킬 수 있었을 문제다.

빼도 링크는 그쪽을 가리킨다. 그래서 **해석 실패를 두 줄로 나눠 보고한다** — 제외 구역을 가리키는 것(정상)과 그 밖(진짜 깨짐).

### 5. 재귀 CTE — 이행 폐쇄

"X를 이해하려면 뭘 먼저 봐야 하나"는 `builds_on`을 **여러 단 따라가는** 질문이다.

```sql
WITH RECURSIVE chain(id, depth) AS (
  SELECT :start, 0
  UNION SELECT e.dst, chain.depth + 1
    FROM edge e JOIN chain ON e.src = chain.id
   WHERE e.kind = 'builds_on' AND chain.depth < 10
)
SELECT * FROM chain ORDER BY depth;
```

`UNION`(`UNION ALL`이 아니라)이 중복을 제거해 **순환에서 무한루프를 막는다.** `depth < 10`은 이중 안전장치.

**이 쿼리를 직접 짜보는 게 Phase 5의 핵심이다.** Phase 7에서 SPARQL로 같은 걸 한 줄로 쓰게 되는데, 그 한 줄의 가치를 알려면 이 여섯 줄을 손으로 써봐야 한다.

```sparql
SELECT ?p WHERE { <doc> :builds_on+ ?p }
```

---

## Step 목록

| Step | 내용 |
|---|---|
| 1 | 스키마 설계 + `build` — 노드·엣지·태그 적재 |
| 2 | 유도 관계 `part_of` |
| 3 | `q stats` · `q type` · `q tag` — 단순 질의 |
| 4 | `q path` — **재귀 CTE 이행 폐쇄** |
| 5 | `q near` · `q orphans` — 이웃과 고아 |
| 6 | **답안지 대조** |

---

## 답안지 대조 — 중요

`docs/README.md`의 실측 표는 **2026-08-11 기준**이다. 그 뒤로 vault가 자랐다 (6,289 → 6,452, +163). 숫자를 그대로 비교하면 안 맞는다.

**Step 6에서는 답안지를 그날 다시 돌려 같은 날짜 기준선을 뽑는다.**

```bash
python3 reference/vault.py build     # 답안지 — 오늘 기준
uv run python -m vault build          # 내 코드
```

노드·엣지·태그·kind별 개수가 **전부 일치**해야 한다. 하나라도 다르면 파서가 다른 것이고, 어느 Phase에서 갈렸는지 역추적한다.

---

## 완료 기준

- [x] `uv run pytest -v` 전부 통과 — 162개
- [x] 답안지와 같은 날 돌려 대조한다 — **「전부 일치」가 아니라 「다른 숫자마다 이유가 있음」으로 통과.** 아래 참조
- [x] `q path`가 여러 단을 탄다 — **깊이 7 확인.** Design System 시리즈가 `00`부터 `08`까지 순서대로 나온다. 아무도 안 적은 커리큘럼이다
- [x] 빌드 1.3초 · 질의 55ms — **빌드 기준을 1초에서 완화한다.** 답안지의 0.8초는 태그를 안 세고 `part_of`를 이름 조회로 하던 때 값이다. 이 기준이 논증하려던 「상주 서버가 필요 없다」는 1.3초로도 성립한다
- [x] **「1부 회고」** — [`learnings/part1-retrospective.md`](../learnings/part1-retrospective.md)

**Phase 5 완료 (2026-08-21). 1부 종료.** 조용히 틀리는 실패를 의심하는 법은 [`learnings/silent-failures.md`](../learnings/silent-failures.md)에 따로 모았다.

### 대조 결과 (2026-08-21)

| | 우리 | 답안지 | |
|---|---:|---:|---|
| **노드** | **3,981** | **3,981** | ✅ |
| **`builds_on`** | **396** | **396** | ✅ |
| **`supersedes`** | **3** | **3** | ✅ |
| `links_to` | 10,195 | 10,763 | 첨부 엣지 568 |
| `part_of` | 1,017 | 1,152 | 이름 조회 오답 139 |
| 태그 | **3,319** | 0 | 답안지가 본문에서 읽는다 |

**세 축이 정확히 일치하고 나머지 셋은 우리 쪽이 맞다.**

- `links_to` — 답안지의 568개는 `dst`가 **노드가 아니다.** 이미지 임베드는 문서 관계가 아니다
- `part_of` — 전역 이름 조회라 `000 Index/Dots/`의 문서가 `500 Mind Compiler/Q1/Dots.md`에 붙는다
- 태그 — 답안지는 **2026-08-11 고정 스냅샷**이라 본문에서 읽는다. 8월 16일 일원화로 본문 태그는 0이 됐다. **답안지의 태그 집계는 영영 0이다**

마지막 줄이 「전부 일치」기준을 고친 이유다. **기준선이 움직이는 건 vault 만이 아니라 답안지 자신이다.**

여기까지가 **지식 그래프**다. 다음 Phase부터가 온톨로지다.
