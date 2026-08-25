# Phase 12 — 핵심 도메인 온톨로지 0.1

> 문서 구조가 아니라 Vault가 다루는 지식 세계를 최소 어휘로 명세한다.

## 목표

Phase 10의 역량 질문과 Phase 11의 정체성 계약을 바탕으로 작은 TBox를 만든다.
개발 지식 전용 스키마가 아니라 Vault 전체가 공유할 **영역 중립 kernel**과, 필요한
영역에서만 붙는 vocabulary/profile의 경계를 설계한다.
후보는 다음과 같지만 질문에 쓰이지 않는 것은 넣지 않는다.

```text
KnowledgeArtifact
Concept
Claim
Event
Decision
Principle
Procedure
Project
```

개인 경험·성찰·철학 표본을 검토한 뒤 다음 후보가 독립 클래스인지 상태·관계인지
판정한다.

```text
Belief · Value · Question · Interpretation · PersonalExperience
```

기술적 `Claim`과 개인적 `Belief`는 모두 문장으로 표현될 수 있지만 진리 조건이
다르다. 개인적 생각에는 주체·관점·시점·경험 맥락을 보존하고, 객관적 사실처럼
무맥락하게 전파하지 않는다.

관계 후보:

```text
expresses · supports · contradicts · derivedFrom · observedIn
appliesTo · requires · operationalizedBy · supersedes
invalidates · hasEvidence · affects
```

## Step 1 — 어휘 요구사항을 질문에서 역추적한다

각 클래스와 속성에 다음을 기록한다.

- 어떤 역량 질문이 이것을 요구하는가
- 자연어 정의와 포함·제외 사례
- 정의역과 치역
- 반례
- 표준 어휘를 재사용하지 않은 이유
- 예상되는 추론

질문이 하나도 연결되지 않는 어휘는 삭제한다.

## Step 2 — 표준 어휘 재사용 범위를 정한다

우선 검토:

- Dublin Core Terms — 문서 메타데이터와 참조
- SKOS — 느슨한 주제·개념 체계
- PROV-O — Entity·Activity·Agent와 출처 계보
- OWL/RDFS — 클래스·속성·논리 공리

표준과 이름이 비슷하다는 이유만으로 재사용하지 않는다. 실제 의미와 제약이 맞는지
확인하고, 맞지 않으면 로컬 어휘를 만들되 연결 근거를 남긴다.

## Step 3 — 추론과 검증을 분리한다

| 요구 | 위치 |
|---|---|
| `Principle`은 `KnowledgeEntity`다 | RDFS/OWL |
| `operationalizedBy`의 역관계 | OWL 또는 질의 |
| 원칙에는 근거가 최소 하나 있어야 한다 | SHACL, Phase 15 |
| 폐기 근거에 의존하면 재검토한다 | 운영 규칙, Phase 16 |
| 승인되지 않은 제안은 확정 사실이 아니다 | 데이터셋 경계, Phase 14 |

특히 domain/range는 검증 규칙이 아니다. Phase 9에서처럼 과도한 선언이 잘못된 타입을
대량 추론할 수 있으므로 필요한 경우에만 둔다.

## Step 4 — 모듈과 버전 정책을 정한다

한 파일에 모두 넣기보다 책임별 모듈을 검토한다.

```text
ontology/
├── artifact.ttl
├── knowledge-kernel.ttl
├── profiles/
│   ├── engineering.ttl
│   └── personal-philosophy.ttl
├── provenance.ttl
└── alignments.ttl
```

실제 파일 구조는 이 Phase에서 확정한다. 다음은 반드시 결정한다.

- ontology version IRI
- 변경 로그
- deprecated term 처리
- 데이터 migration 필요 여부
- import를 네트워크 없이 재현하는 방법

## Step 5 — 논리 일관성과 질문 적합성을 테스트한다

- Turtle 파싱 테스트
- 기대한 subclass·inverse·subproperty 테스트
- 의도하지 않은 유형 추론 테스트
- 모순 사례 테스트
- 각 역량 질문에 필요한 graph pattern 작성
- 전체 ontology closure 크기와 시간 측정

## 산출물

- 핵심 온톨로지 0.1
- 어휘별 competency mapping
- 재사용 표준과 로컬 어휘 결정 기록
- ontology version·deprecation·migration 정책
- 논리 회귀 테스트

## 완료 조건

- [ ] 클래스 8~12개, 핵심 관계 10~15개 이내에서 시작한다.
- [ ] 모든 어휘가 실제 역량 질문에 연결된다.
- [ ] 문서 역할 클래스와 지식 개체 클래스가 섞이지 않는다.
- [ ] 기술 주장과 믿음·가치·해석의 인식적 지위가 섞이지 않는다.
- [ ] 공통 kernel이 특정 Vault 대역의 분류 체계를 강요하지 않는다.
- [ ] 검증·운영 상태를 OWL로 억지 표현하지 않는다.
- [ ] 의도하지 않은 domain/range 유형 추론이 없다.
- [ ] Phase 1~9 회귀 테스트가 통과한다.

## 난이도와 위험

**난이도: 높음. 코드는 작지만 모델 오류의 파급 범위가 크다.**

이 단계의 위험은 구현 버그보다 의미가 그럴듯하게 틀리는 것이다. 속성 하나를
Transitive로 선언하거나 domain을 넓게 잡으면 수천 개의 사실이 조용히 바뀔 수 있다.
그래서 긍정 테스트뿐 아니라 "절대 추론되면 안 되는 것"을 고정하는 부정 테스트가
필수다. 특히 개인의 관점에서 나온 해석이 전역 객관 사실로 추론되지 않는 사례를
부정 테스트에 넣는다.
