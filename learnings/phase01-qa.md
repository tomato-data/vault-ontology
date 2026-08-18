# Phase 1: Q&A

frontmatter 파서를 짜면서 나온 질문과 답.

## 스키마

### Q: `builds_on`, `supersedes`가 정확히 뭘 의미하나?

vault 스키마 정본이 **이름 붙인 관계는 이 둘뿐**이라고 못박았다.

**`builds_on` — 선행 지식.** "이 문서는 저 문서 위에 세워졌다."

```yaml
# CIDR.md
builds_on:
  - "[[Subnet mask]]"
```

`Subnet mask`를 모르면 `CIDR`을 읽어도 안 들어온다. 화살표는 나중 것에서 먼저 것으로 간다. 후속 문서가 자기 토대를 가리킨다.

- 이행적. A가 B 위에, B가 C 위에면 A는 C 위에도 있다
- 실측 최대 깊이 7 · 387건
- 상한 3개. 「수집은 원본의 10%」에서 나온 숫자다. 열 개씩 달면 선행 지식이 아니라 관련 문서 목록이다

이행성 덕에 "X를 이해하려면 뭘 먼저 읽나"가 풀린다. 답안지의 `vault q path`가 재귀 CTE로, Phase 7이 SPARQL `builds_on+`로, Phase 9가 추론 물질화로 **같은 질문을 세 번 푼다.**

**`supersedes` — 대체.** "이 문서가 저 문서를 갈아치웠다." 3건.

| | `builds_on` | `supersedes` |
|---|---|---|
| 축 | 논리 | 시간 |
| 대상의 운명 | 둘 다 살아 있다 | 대상은 은퇴한다 |
| 읽기 | 둘 다 읽어야 한다 | 새 것만 읽으면 된다 |

### Q: 왜 이 둘만 이름을 받았나?

위키링크 24,969개는 "여기서 저기를 언급했다"만 말한다. 방향은 있는데 의미가 없다. 참고인지 반박인지 예시인지 알 수 없다.

이름이 있으면 **추론의 재료가 된다.**

```
A builds_on B, B builds_on C  →  A builds_on C     참
A links_to  B, B links_to  C  →  A links_to  C     헛소리
```

의미를 주장할 수 있는 관계만 이름을 받는다. 나머지는 무명으로 둔다. Phase 8에서 `supersedes`를 표준 어휘(`dcterms:replaces`)와 맞출지 판단하게 된다.
