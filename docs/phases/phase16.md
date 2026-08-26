# Phase 16 — SHACL 의미 계약

> OWL이 추론하는 것과 Vault가 요구하는 것을 분리한다.

## 목표

Phase 4의 Python lint가 문서 스키마를 검사하듯, SHACL은 의미 그래프의 구조와 필수
관계를 검사한다. OWL의 열린 세계 가정으로 표현할 수 없는 요구를 SHACL에 둔다.

초기 shape 후보:

- `Principle`은 승인된 근거를 최소 하나 가진다.
- `Decision`은 결과와 판단 근거를 가진다.
- `Claim`은 근거 artifact 위치를 가진다.
- `supersedes`의 주체와 대상은 같지 않다.
- `operationalizedBy`의 대상은 `Procedure`다.

## Step 1 — 기존 lint와 중복 범위를 정한다

기존 lint를 즉시 SHACL로 교체하지 않는다.

| 규칙 | 우선 구현 |
|---|---|
| frontmatter 날짜 형식 | Python lint 유지 |
| 위키링크 해석 | Python lint 유지 |
| RDF artifact에 abstract가 있는가 | parity 실험 |
| Principle의 evidence | SHACL 신규 |
| Decision의 semantic relation | SHACL 신규 |

같은 규칙을 양쪽에 구현할 때는 같은 fixture에서 결과가 일치해야 한다.

## Step 2 — shape를 RED 테스트로 작성한다

각 shape에 네 fixture를 둔다.

1. 통과하는 최소 그래프
2. 필수 값이 빠진 그래프
3. 타입이 잘못된 그래프
4. 경계값 또는 예외 그래프

위반 경로, severity, 사람이 읽는 메시지까지 테스트한다.

## Step 3 — 경고와 거부를 분리한다

- Violation: 승인 그래프에 들어갈 수 없음
- Warning: 들어갈 수 있으나 검토 필요
- Info: 개선 제안

처음부터 모든 shape를 거부 규칙으로 만들지 않는다. 기존 393개 lint 위반처럼 누적된
부채가 도입 자체를 막지 않도록 신규·변경 assertion과 전체 감사 모드를 구분한다.

## Step 4 — SHACL 보고서를 원문에 연결한다

보고서는 IRI만 출력하지 않는다.

```text
문서 경로
section/block
위반한 지식 개체
shape와 메시지
관련 근거
수정 방향
```

## Step 5 — 성능과 coverage를 측정한다

- 50개 gold set
- 500개 확대 표본
- 전체 Vault 파생 그래프

각 단계에서 실행 시간, 오탐, 누락, 위반 분포를 기록한다. 엔진 교체는 실제 병목이
나온 뒤에만 검토한다.

## 산출물

- SHACL shapes 5개 이상
- shape fixture와 parity 테스트
- 사람이 읽는 검증 보고서
- 신규/변경 검증과 전체 감사 모드
- 성능·오탐·누락 측정

## 완료 조건

- [ ] 초기 shape가 gold set의 기대 위반과 일치한다.
- [ ] 기존 lint와 겹치는 규칙은 결과가 일치한다.
- [ ] OWA 추론과 닫힌 세계 검증이 코드와 문서에서 분리되어 있다.
- [ ] 위반에서 원문 위치로 바로 돌아갈 수 있다.
- [ ] 전체 Vault의 기존 부채가 신규 assertion 생성을 전부 막지 않는다.

## 난이도와 위험

**난이도: 중상. 기술보다 규칙 강도가 어렵다.**

SHACL 문법 자체보다 무엇을 필수로 볼지가 더 어렵다. 지나치게 강한 shape는 유효한
지식을 거부하고, 약한 shape는 형식만 갖춘 빈 데이터를 통과시킨다. 초기에는 실제로
사람이 수정할 의향이 있는 규칙만 넣는다.
