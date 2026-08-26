# Phase 13 — 문서와 지식 개체의 분리

> `type: principle`인 파일과 실제 원칙은 같은 것이 아니다.

## 핵심 문제

현재 `v:Concept`, `v:Decision`, `v:Principle`은 모두 Markdown 문서의 유형이다.
3부에서 같은 이름을 실제 개념·결정·원칙에 재사용하면 다음 두 사실이 구분되지 않는다.

```text
문서를 다른 파일에 합쳤다
원칙 자체를 폐기했다
```

문서는 표현물이고, 지식 개체는 문서가 표현하는 대상이다. Phase 13은 이 둘의
정체성과 수명 주기를 분리한다.

## 목표 모델

```text
KnowledgeArtifact          KnowledgeEntity
├── MarkdownDocument       ├── Concept
└── Section/Block          ├── Claim
                           ├── Event
document expresses ───────→├── Decision
                           ├── Principle
                           └── Procedure
```

이 그림은 방향이지 아직 확정 어휘가 아니다. Phase 10의 질문으로 필요한 것만 남긴다.

## Step 1 — 현재 클래스의 의미를 명시한다

기존 13개 `type`은 문서 역할로 보존한다. 기존 `v:Principle`을 조용히 실제 원칙
클래스로 바꾸지 않는다.

선택지를 비교한다.

1. 기존 클래스를 `PrincipleDocument`처럼 명시적으로 개명하고 호환 공리를 둔다.
2. 기존 문서 어휘 네임스페이스를 유지하고 지식 개체를 새 네임스페이스에 둔다.
3. 문서 `type`을 클래스 대신 역할 값으로 모델링한다.

선택 기준은 기존 RDF 소비자 호환성, 질의 명료성, 마이그레이션 비용이다.

## Step 2 — 의미 개체의 최소 단위를 정한다

다음 사례를 모두 표현할 수 있어야 한다.

- 한 문서에 주장 세 개가 있다.
- 같은 개념을 여러 문서가 설명한다.
- 한 원칙 문서 안에 원칙과 예외가 함께 있다.
- 문서가 이동하거나 이름이 바뀐다.
- 문서 두 개가 하나로 합쳐지거나 하나가 둘로 나뉜다.
- 같은 문장을 다듬었지만 주장의 정체성은 유지된다.

문장 해시만으로 ID를 만들면 문장 수정 시 정체성이 바뀐다. 파일 경로만 쓰면 이동과
분할을 견디지 못한다. 최소 단위와 ID 수명 주기를 함께 정해야 한다.

## Step 3 — 안정 ID 정책을 실험한다

후보:

- Markdown frontmatter의 명시적 ID
- Obsidian block ID
- 섹션 anchor + 문서 ID
- 별도 sidecar manifest
- 승인 시 발급하는 불투명 ID

평가 시나리오:

```text
rename document
move document
edit claim text
split document
merge documents
delete artifact but retain knowledge entity
```

각 시나리오에서 어떤 IRI가 유지되고 어떤 provenance 이벤트가 생기는지 테스트한다.

## Step 4 — IRI와 네임스페이스 계약을 정한다

최소한 다음 공간을 구분한다.

- 문서·섹션 같은 산출물
- 개념·주장·사건·원칙 같은 지식 개체
- 어휘와 공리
- 제안·승인·추론 활동

현재 path 기반 `doc_iri`는 문서 그래프의 호환 경로로 남길 수 있다. 새 지식 개체의
ID까지 path 기반으로 만들지는 않는다.

## Step 5 — 호환 계층을 설계한다

- Phase 6~9의 테스트를 그대로 통과시킨다.
- 기존 `.vault.ttl` 소비자가 갑자기 다른 의미를 받지 않게 한다.
- 이전 IRI에서 새 IRI로 가는 명시적 매핑 또는 migration을 둔다.
- deprecated 어휘는 삭제하지 말고 버전과 대체 관계를 기록한다.

## 산출물

- `docs/semantic-identity.md`
- artifact와 knowledge 네임스페이스 결정
- rename·move·split·merge에 대한 ID 테스트
- 기존 문서 클래스와 새 지식 클래스의 대응표
- 호환성 및 migration 정책

## 완료 조건

- [ ] 문서와 실제 개념·주장·원칙이 서로 다른 리소스다.
- [ ] 한 문서의 여러 주장과 여러 문서의 한 개념을 표현할 수 있다.
- [ ] rename·move에서 지식 개체 ID가 유지된다.
- [ ] split·merge의 출처 계보를 잃지 않는다.
- [ ] 기존 Phase 1~9 테스트가 모두 통과한다.
- [ ] 같은 로컬 이름을 다른 의미로 조용히 재사용하지 않는다.

## 난이도와 위험

**난이도: 높음. 다만 Phase 10 조사 뒤 압박이 내려갔다.**

Phase 6의 IRI는 파일 경로를 안정적으로 되돌리는 문제였다. Phase 13의 ID는 편집·이동·
분할 뒤에도 같은 의미를 가리켜야 한다. 잘못 선택하면 이후 모든 relation과 provenance를
마이그레이션해야 한다. 구현 속도보다 사례표와 migration 테스트에 시간을 더 써야 한다.

> **선행 관측 — [`part3-decisions.md`](../part3/decisions.md)의 관측 1~4**
>
> - **마이그레이션할 데이터가 0개다.** 판단끼리의 관계가 8건(템플릿 생성분 제외),
>   근거 관계는 없고, `supersedes` 5건은 전부 대상이 없다. gold set 이전까지
>   ID 정책은 사실상 되돌릴 수 있다. **Phase 11·13에 시간을 더 쓴다.**
> - **이미 쓰는 앵커가 가장 부서지기 쉽다.** `500/Q7/_Patterns.md`가 근거를
>   `[[문서]] 4행`으로 가리킨다. 행 번호 앵커를 시나리오 테스트에 반드시 넣는다.
> - **시험 사례가 실물로 있다.** `900 Archive/Mind Compiler/`의 Q3는 경로가 바뀌고
>   상태가 종결됐는데 결론은 현재 Q7·Q2에서 살아 있다. 가상 fixture보다 먼저 쓴다.
> - **frontmatter 단독 ID는 900에 못 쓴다.** 210개 전부 frontmatter가 없다.
