# Phase 7: Q&A

> SPARQL. Phase 5에서 SQL로 푼 질문을 다시 푼다.

## 패턴/설계

### Q: property path가 짧은데 왜 위험한가

경로 연산자(`+` `*` `^` `/` `|`)는 재귀·역방향을 한두 글자로 줄인다.
짧아서 좋지만, 방향을 틀리면 **에러 없이 절반만 맞는 답**을 낸다.

- `^skos:broader*` vs `skos:broader*` — 캐럿 하나로 계층을 거꾸로 타서
  중첩 태그를 놓쳤다. 빈 결과라 조용하다.
- 그래서 `test_the_two_engines_agree`처럼 SQLite와 대조하는 테스트가
  값지다. 정답지 없이는 그럴듯한 오답을 못 잡는다.

### Q: SPARQL SELECT는 집합인가

아니다. **bag**이다. 같은 결과가 여러 경로로 매칭되면 여러 번 나온다.
양방향 이웃을 `v:links_to|^v:links_to`로 구하면, 양쪽 다인 문서가 두 번
잡힌다. `DISTINCT`가 필요하다 — SQL `UNION`이 자동으로 하던 일이다.

## Python

### Q: str.maketrans로 만든 dict를 뒤집으면 왜 값이 정수인가

`str.maketrans({" ": "%20"})`는 `{32: "%20"}`를 만든다. key가 문자가
아니라 **코드포인트(정수)**다. `translate`가 정수 key로 매핑하기 때문.
그래서 `{v: k for k, v in ...}`로 뒤집으면 `{"%20": 32}` — 값이 정수다.
`chr(32)`로 문자를 되살려야 `replace`에 쓸 수 있다.
