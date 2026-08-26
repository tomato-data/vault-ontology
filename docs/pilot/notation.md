# Phase 11 파일럿 — 임시 표기

> **정식 문법이 아니다.** 버릴 것이다. 목적은 세 형식 중 어느 쪽이 덜 괴로운지
> 몸으로 아는 것이다. 어휘는 [`relations-v0.md`](../part3/relations-v0.md), 문서는
> [`pilot-set.md`](set.md).

## 세 형식

### A · frontmatter 확장

기존 `builds_on`·`supersedes`와 같은 자리다. `vault/graph.py:83`이 이미 이 모양을
읽으므로, 필드 이름만 늘리면 기존 SQLite가 그대로 받는다.

```yaml
---
type: principle
summary: …
created: 2026-04-17
derived_from:
  - "[[테스트 스위트 성능 — 측정 우선, 루프≠게이트, 검사량 축소]]"
diverges_from:
  - "[[A Philosophy of Software Design]]"
source_unknown: true
---
```

- **장점** — 눈에 보이고 git diff가 명확하다. 기존 도구가 바로 읽는다.
- **의심** — 문서 단위보다 세밀해질 수 없다. 「이 원칙의 3번 조항이 저 사건에서 나왔다」를 못 쓴다.

### B · 본문 전용 섹션

문서 맨 아래에 `## 의미` 섹션을 붙인다. 근거 위치를 함께 적을 수 있다.

```markdown
## 의미

- derived_from → [[테스트 스위트 성능 — 측정 우선…]] §「측정 우선」
- applies → [[Frontend 테스트는 환경 부팅 비용을 먼저 측정하라]]
- violates → [[간단한 서비스에 과잉 인프라를 구축하지 마라]]  # 초기 판단
- as_of → 2026-02
```

- **장점** — 섹션·문단을 가리킬 수 있다. 사람이 읽고 고치기 쉽다.
- **의심** — 본문을 오염시킨다. 읽는 흐름을 끊는다.

### C · sidecar

vault를 건드리지 않고 저장소에 따로 둔다. 파일은
`experiments/pilot/labels/<번호>-<짧은이름>.md`.

```markdown
# 8 · 500 Q1 _Insights

문서: 500 Mind Compiler/Q1. Better Developer/_Insights.md

## 인사이트 3
- expresses → 가치:본질탐구
- as_of → 2026-03-08

## 인사이트 7
- informs → [[기술적 의사결정을 어떻게 내리는가?]]
- as_of → 2026-05-24
```

- **장점** — 본문이 깨끗하다. **문서 안의 항목을 자유롭게 가리킬 수 있다.**
- **의심** — 원문과 어긋나기 시작한다. 문서를 고치면 sidecar가 낡는다.

---

## 배정

각 형식이 쉬운 것과 어려운 것을 골고루 받도록 섞었다.

| 문서 | 형식 | 왜 |
|---|---|---|
| 1 Decision Node - Pragmatic vs Clean | **A** | 관계가 적다. frontmatter로 충분한지 본다 |
| 2 Decision Node - Architecture Style | **A** | 1번과 같은 형식이라야 비교가 된다 |
| 3 Frontend 테스트는 환경 부팅 비용을… | **A** | `source_unknown`을 frontmatter로 쓸 수 있는지 |
| 4 테스트 스위트 성능 (302.8 Learnings) | **B** | 원칙 4개 중 무엇을 따르고 어겼는지 **근거 위치가 필요하다** |
| 5 웹 개발자를 위한 소프트웨어 설계 원칙 | **B** | 저자와 바꾼 지점을 문단 단위로 가리켜야 한다 |
| 6 A Philosophy of Software Design | **C** | 챕터 22개짜리 대표노트. 본문을 건드리기 싫다 |
| 7 Case Study - Ousterhout의 TDD 비판 | **B** | 5·6번과 한 계보. 세 형식이 섞이면 비교가 흐려지니 B로 |
| 8 500 Q1 _Insights | **A · B · C 전부** | **번호 매겨진 항목 다수. 여기가 결판난다** |
| 9 900 Q3 _Question | **A** | `status: archived`를 frontmatter로 쓰는 게 자연스러운지 |
| 10 모든 정답은 일시적이다 | **C** | 개인 문서. 본문에 라벨이 섞이는 게 견딜 만한지 |
| 11 시라트를 본 후 정호와의 대화 | **B** | 10번과 다른 형식이라야 개인 대역 안에서 비교가 된다 |

**8번을 세 형식 모두로 적는다.** 문서 하나에 항목이 여럿인 경우가 3부의 규모를
가르는 지점이므로, 여기서만은 세 형식을 나란히 놓고 본다. **시간도 따로 잰다.**

---

## 규칙

1. **완벽하게 적으려 하지 마라.** 애매하면 애매하다고 적고 넘어간다. 보류 비율이 측정 대상이다.
2. **시간을 잰다.** 문서 하나마다 시작·끝 시각을 [`pilot-log.md`](log.md)에 적는다.
3. **근거를 가리키는 데 필요했던 단위**를 매번 적는다 — 문서 / 섹션 / 블록·행. **이게 제일 중요하다.**
4. 없는 관계를 억지로 만들지 마라. 어휘 12개가 안 쓰이면 안 쓰인 대로 둔다.
5. 사적 내용은 저장소로 옮기지 않는다 (D6). 10·11번의 sidecar·본문 라벨에 인용을 넣지 않는다.

## 되돌리기

A와 B는 vault 파일을 고친다. **파일럿이 끝나면 되돌린다.**

```bash
cd "$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault"
git diff --stat          # 무엇이 바뀌었는지
git checkout -- <파일>    # 되돌리기
```

시작 전에 vault를 커밋해두면 되돌리기가 확실하다.
