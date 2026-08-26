# Phase 15 — 의미 사실 그래프 빌더

> 승인된 의미 입력을 재현 가능한 ABox와 provenance로 변환한다.

## 목표

Phase 12의 작성 계약을 읽어 다음 세 층을 분리한 데이터셋을 만든다.

```text
asserted graph    사람이 승인한 사실
proposed graph    미승인 제안
inferred graph    다시 계산 가능한 파생 사실
```

Markdown은 계속 정본이며 그래프는 전부 다시 만들 수 있어야 한다.

## Step 1 — 입력 파서를 테스트로 고정한다

- 문서·섹션·block ID 파싱
- knowledge entity ID 해석
- 관계 대상 해석
- 근거 위치 보존
- 중복 assertion의 집합 처리
- 삭제·rename·split·merge 처리
- 잘못된 문법의 명시적 거부

현재 `build_graph`를 무리하게 확장할지 새 semantic builder를 둘지는 결합도와 회귀
위험을 측정한 뒤 결정한다. 기존 문서 그래프가 새 의미 그래프에 종속되게 만들지 않는다.

## Step 2 — 출처를 사실과 함께 저장한다

최소 provenance:

- 원본 artifact와 block/section
- assertion을 만든 주체
- 생성·승인 시점
- 사용한 도구 또는 모델과 버전
- asserted·proposed·inferred 상태
- 이전 assertion을 대체하거나 철회한 활동
- 주관적 진술의 관점 주체와 유효 시점
- 해석이 적용되는 프로젝트·생활·철학 맥락

PROV-O를 우선 검토하되, 질의가 지나치게 복잡해지면 로컬 profile을 정의한다.

## Step 3 — 그래프 경계를 구현한다

rdflib `Graph` 하나에 상태를 섞지 않는다. `Dataset`/named graph, 별도 산출물, 상태
predicate 가운데 실제 질의와 저장 형식에 맞는 방식을 실험한다.

필수 불변식:

- proposed 사실은 기본 질의에 나타나지 않는다.
- inferred graph는 asserted graph에서 재생성할 수 있다.
- assertion 철회가 원본 근거를 삭제하지 않는다.
- 같은 빌드를 두 번 실행해도 결과가 같다.
- 한 관점의 `Belief`가 무맥락한 전역 `Claim`으로 승격되지 않는다.

## Step 4 — 증분보다 정확성을 먼저 검증한다

초기 구현은 전체 재빌드로 시작한다. 50개 기준 집합과 전체 Vault 일부를 실측한 뒤
병목이 확인될 때만 증분 갱신을 검토한다.

## Step 5 — 기존 그래프와 연결한다

- artifact IRI에서 기존 `doc_iri`로 왕복한다.
- 기존 type·tag·folder·wikilink 사실을 중복 생성하지 않는다.
- 기존 SQLite 질의와 RDF 산출물 결과를 보존한다.
- 의미 그래프가 없어도 기존 CLI가 정상 동작한다.

## 산출물

- semantic assertion parser
- asserted·proposed·inferred graph 분리
- provenance profile
- gold graph 재현 테스트
- 전체 재빌드 명령과 측정 결과

## 완료 조건

- [ ] 기준 데이터의 asserted graph를 정확히 재현한다.
- [ ] 모든 의미 assertion에서 원문 근거로 돌아갈 수 있다.
- [ ] proposed 사실이 확정 질의에 섞이지 않는다.
- [ ] 빌드가 결정론적이고 멱등적이다.
- [ ] 기존 그래프와 Phase 1~9 테스트가 깨지지 않는다.
- [ ] 그래프 파일을 지우고 Markdown에서 전부 복원할 수 있다.

## 난이도와 위험

**난이도: 높음. 데이터 모델과 상태 모델이 동시에 들어온다.**

현재 그래프는 파일에서 단방향으로 재생성하면 끝난다. 새 그래프는 승인·철회·출처를
보존해야 해 시간축이 생긴다. 이력을 파생 데이터에만 두면 재빌드 시 사라지고, 모두
Markdown에 넣으면 작성 부담이 커진다. 이 경계를 Phase 12의 실측 없이 정하면 안 된다.
