# Phase 19 — 제안·승인·철회 워크플로우

> 자동화는 의미 사실을 확정하지 않고 검토 가능한 제안을 만든다.

## 목표

규칙 또는 LLM이 다음을 제안할 수 있게 하되, 승인 전에는 확정 그래프와 Markdown에
영향을 주지 않게 한다.

- 문서가 표현하는 지식 개체
- `supports`·`contradicts`·`derivedFrom` 관계
- 중복 가능성이 있는 개념이나 주장
- 교훈의 원칙 승격 후보
- 폐기 근거에 의존하는 재검토 후보

## Step 1 — 제안 객체를 정의한다

최소 필드:

```text
proposal_id
proposed assertion
source artifact/block
evidence excerpt or relation path
producer and model/version
created time
confidence as a signal, not truth
status: pending/approved/rejected/superseded
reviewer and reason
```

동일 제안을 반복 생성했을 때 중복되지 않도록 안정된 fingerprint를 둔다.

## Step 2 — 생성기와 승인기를 분리한다

- 생성기는 proposed graph에만 쓴다.
- 승인기는 asserted graph 또는 Markdown 정본 반영을 담당한다.
- 생성기는 승인 권한을 갖지 않는다.
- 승인 과정은 원문 diff와 예상 graph diff를 함께 보여준다.
- 거절 이유를 보존해 같은 오탐을 측정하고 줄인다.

## Step 3 — 작은 생성기부터 시작한다

우선순위:

1. 결정론적으로 검출할 수 있는 누락 관계
2. 명시 링크와 문장 패턴에 근거한 후보
3. LLM 기반 의미 관계 후보

LLM은 마지막에 붙인다. gold set에서 precision·recall과 검토 시간을 측정하고, 높은
confidence도 자동 승인의 근거로 사용하지 않는다.

### 민감한 문서 경계

Vault 전체를 대상으로 하므로 100 Private Log, 커리어, 회사 프로젝트 문서가 제안
입력에 포함될 수 있다. 생성기를 붙이기 전에 다음을 결정한다.

- 기본은 로컬 처리인지
- 외부 모델에 보낼 수 있는 대역과 금지 대역
- 프롬프트·응답·trace가 어디에 저장되는지
- 모델 제공자에게 보낸 원문을 감사할 수 있는지
- 민감한 근거 excerpt를 제안·로그에 얼마나 남길지

승인되지 않은 외부 반출은 relation 오탐보다 더 큰 실패다. 대역별 정책이 없으면
LLM 생성기를 실행하지 않는다.

## Step 4 — 승인·거절·철회를 테스트한다

필수 시나리오:

- 제안 승인 후 재빌드
- 제안 거절 후 같은 입력 재처리
- 승인 사실의 철회
- 문서 rename·split 후 pending 제안 재연결
- 모델 버전 변경 후 재제안
- 동시에 생성된 상충 제안

## Step 5 — 검토 비용을 성공 지표에 넣는다

- 제안 승인율
- 관계 종류별 precision/recall
- 제안 한 건 검토 시간
- 반복 오탐 비율
- 제안으로 절약된 작성 시간
- 잘못 승인한 사실의 수정 비용

제안이 늘어났지만 검토 부담이 더 커졌다면 실패다.

## 산출물

- proposal model과 저장소
- 생성·검토·승인·거절·철회 API
- 원문 diff와 graph diff preview
- provenance와 audit log
- gold set 기반 품질 및 검토 비용 보고서

## 완료 조건

- [ ] 승인 전 제안은 확정 질의와 Markdown에 영향을 주지 않는다.
- [ ] 모든 제안에 근거와 생성 주체가 있다.
- [ ] 승인·거절·철회가 감사 가능하다.
- [ ] 같은 제안이 반복 누적되지 않는다.
- [ ] 잘못 승인한 사실을 복구할 수 있다.
- [ ] 제안의 순효용이 검토 비용보다 크다.
- [ ] 민감 문서의 모델·로그·반출 정책이 명시적으로 적용된다.

## 난이도와 위험

**난이도: 매우 높음. 정확도 문제가 데이터 거버넌스 문제로 바뀐다.**

현재 파서는 틀리면 재빌드하면 된다. 승인된 의미 사실이 틀리면 이후 추론과 판단이
연쇄적으로 오염된다. confidence threshold만으로 해결할 수 없고, 상태 분리·감사·철회가
기능의 본체가 된다.
