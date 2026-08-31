# gold set 답안 — 1차 50개

> Phase 12 Step 4. 2026-08-31.
> **Phase 15 의 파서는 이 답을 재현해야 한다.** 관계는 vault frontmatter 에 실제로
> 적혀 있고, 여기 있는 것은 그 목록과 **관계가 없다고 판정한 이유**다.
>
> 목록은 [`gold-set-manifest.md`](gold-set-manifest.md).

## 집계

```
문서 50 · 의미 관계를 가진 문서 19 (38%)

derived_from     24
informed_by      4
applies          2
expresses        1
diverges_from    1
contradicts      1
answered_by      0   ← 한 번도 안 나왔다
```


## 000 Index — 1 / 3

**`400 Logic Forge`** · `principle`

```yaml
derived_from:
  - experience
```

- `209 Principles 가이드라인` · `procedure` — **관계 없음**
- `0429_tdd_plan_go_post_e2e_분석` · `concept` — **관계 없음**


## 100 Private Log — 3 / 6

**`모든 정답은 일시적이다`** · `reflection`

```yaml
derived_from:
  - "[[나를 피곤하게 만드는 것들에 반응하지 않는 연습]]"
expresses:
  - "[[500 Mind Compiler/Q7. Who Am I/_Insights#인사이트 20]]"
informed_by:
  - "[[Sapiens]]"
  - "[[이방인의 뫼르소와 나]]"
```

**`이방인의 뫼르소와 나`** · `reflection`

```yaml
derived_from:
  - "[[2026.01.25 다양한 가능성과 변화]]"
```

**`2026-05-20 본질주의와 우월감 회로 자기 점검`** · `reflection`

```yaml
informed_by:
  - "[[나를 피곤하게 만드는 것들에 반응하지 않는 연습]]"
diverges_from:
  - "[[2026-01-26 뫼르소와 나에 대한 성찰 대화]]"
```

- `BNV 솔루션` · `reflection` — **관계 없음**
- `책` · `reflection` — **관계 없음**
- `영상` · `reflection` — **관계 없음**


## 200 Dev Knowledge Base — 5 / 12

**`FastAPI 테스트에서 TestClient를 with로 감싸지 마라`** · `principle`

```yaml
derived_from:
  - experience
```

**`JWT 기반 다중 로그인 제한 패턴`** · `principle`

```yaml
derived_from:
  - "[[다중 로그인 제한 구현 패턴]]"
```

**`DB Connection Pool은 85%까지만, 나머지는 headroom`** · `principle`

```yaml
derived_from:
  - "[[ECS 태스크 스케일링과 DB 풀 최적화 전략]]"
```

**`IO-bound 서비스는 asyncio를 우선하라`** · `principle`

```yaml
derived_from:
  - "[[asyncio 도입 이점]]"
```

**`PostgreSQL 스키마 설계 전략 (public 비우기, 커스텀 스키마 활용)`** · `concept`

```yaml
derived_from:
  - "[[PostgreSQL 스키마 분리 전략]]"
```

- `Ansible 인벤토리 — 호스트 그룹과 -i 옵션` · `concept` — **관계 없음**
- `08 FinOps 실천 — 가시화·약정 관리·자동화` · `concept` — **관계 없음**
- `Heap (힙) — 자료구조` · `concept` — **관계 없음**
- `Heap (힙) — 메모리 영역` · `concept` — **관계 없음**
- `Race Condition` · `concept` — **관계 없음**
- `_개발 규율집 (Project Discipline Bible)` · `principle` — **관계 없음**
- `FastAPI - Swagger UI에서 Bearer 토큰 사용하기` · `procedure` — **관계 없음**


## 300 Runtime — 3 / 8

**`회계 데이터 무결성 4계층 — append-only ledger·마감·provenance·reconciliation`** · `project-doc`

```yaml
derived_from:
  - "[[원비관리 도메인 사후 회고 — classes.student_ids ID 일관성 + 4건 사용자 이슈 (2026-05)]]"
```

- `API 레이어 정리와 헬퍼 중앙화` · `project-doc` — **관계 없음**
**`테스트 스위트 성능 — 측정 우선, 루프≠게이트, 검사량 축소`** · `project-doc`

```yaml
applies:
  - "[[Plan은 가설 모음 — 가정 검증, scope 확장, raw 측정값 보존]]"
  - "[[Frontend 테스트는 환경 부팅 비용을 먼저 측정하라]]"
```

- `bnvsglobal 인프라 진화` · `project-doc` — **관계 없음**
- `Best Practices 감사 및 개선 (2026-04)` · `project-doc` — **관계 없음**
- `2026-08-26` · `log` — **관계 없음**
- `커피챗 기록 — 레브잇 2026-08` · `log` — **관계 없음**
**`01 post — 콘솔에서 IaC까지`** · `project-doc`

```yaml
derived_from:
  - "[[01 뼈대 — 콘솔에서 IaC까지]]"
```



## 400 Logic Forge — 6 / 10

**`Decision Node - Architecture Style Selection`** · `decision`

```yaml
derived_from:
  - "[[Trade-offs - Clean vs Pragmatic Architecture]]"
```

**`Decision Node - Pragmatic vs Clean Architecture`** · `decision`

```yaml
derived_from:
  - "[[400 Logic Forge/401 Architecture Playbook/Layer 2. Backend/Code-Structure/Trade-offs - Pragmatic vs Clean Architecture]]"
  - "[[FastAPI Pragmatic vs Strict Clean Architecture]]"
contradicts:
  - "[[Decision Node - Architecture Style Selection]]"
```

**`Trade-offs - Pragmatic vs Clean Architecture`** · `tradeoff`

```yaml
derived_from:
  - "[[아키텍처 분석 - Clean Architecture 오버헤드와 FSD 전환]]"
  - "[[Conclusion]]"
  - "[[FastAPI Pragmatic vs Strict Clean Architecture]]"
```

- `Case Study - Ousterhout의 TDD 비판과 ODP 통합 TDD의 대응` · `concept` — **관계 없음**
- `Case Study - 테스트 DB 프로비저닝 (testcontainers 병목)` · `case` — **관계 없음**
**`Decision Node - JWT vs Session`** · `decision`

```yaml
derived_from:
  - "[[Trade-offs - JWT vs Session]]"
  - "[[JWT vs Session 벤치마크 분석]]"
  - "[[인증 방식 벤치마크]]"
```

**`Decision Node - Live Activity 종료 폴링 전략`** · `decision`

```yaml
derived_from:
  - "[[Trade-offs - Celery vs APScheduler vs lifespan task]]"
  - "[[앱 강제 종료 시 Live Activity 자동 소멸 설계]]"
  - "[[iOS Live Activity Widget 렌더 트리거의 한계]]"
```

**`Decision Node - 저사양 vCPU 환경의 ASGI 서버 구성`** · `decision`

```yaml
derived_from:
  - "[[Trade-offs - Uvicorn vs Gunicorn]]"
  - "[[서버 구성 벤치마크 (Uvicorn vs Gunicorn)]]"
```

- `Trade-offs - Pragmatic vs Clean Architecture` · `tradeoff` — **관계 없음**
- `Decision Node - Pragmatic vs Clean Architecture` · `decision` — **관계 없음**


## 500 Mind Compiler — 1 / 6

- `_Insights` · `reflection` — **관계 없음**
- `_Patterns` · `reflection` — **관계 없음**
- `_Insights` · `reflection` — **관계 없음**
**`창작은 나에게 어떤 의미인가?`** · `reflection`

```yaml
informed_by:
  - "[[Sirat]]"
```

- `좋은 친구란 무엇인가?` · `reflection` — **관계 없음**
- `Quarterly Synthesis - 2026-Q1` · `reflection` — **관계 없음**


## 600 Content Observatory — 0 / 4

- `기생충` · `review` — **관계 없음**
- `Valheim` · `review` — **관계 없음**
- `3. Abstract Factory — Strategy에 일관성을 부여하는 패턴` · `source-note` — **관계 없음**
- `KAO 방법론` · `source-note` — **관계 없음**


## 900 Archive — 0 / 1

- `_Insights` · `—` — **관계 없음**


---

# 「관계 없음」이 31개인 이유 — 갈래별

**부착률 38%는 낮은 게 아니라 정확한 값이다.** 왜 안 붙었는지가 갈래로 나뉜다.

| 갈래 | 개수 | 예 |
|---|---|---|
| **「관련 문서」 절만 있다** | 12쯤 | 「관련 개념」·「Related」·「관련 노트」 — 무명 위키링크의 몫 |
| **이미 `builds_on` 으로 이어져 있다** | 3 | `08 FinOps 실천` — `builds_on` 3개가 이미 다 잡고 있다 |
| **문서 단위로는 관계가 없다** | 5 | `500` 전부. 관계가 항목에 있다 |
| **본문에 링크가 아예 없다** | 4 | `기생충` · `Valheim` · `FastAPI Swagger UI` · `좋은 친구란` |
| **frontmatter 가 없다** | 1 | `900 Archive/Mind Compiler/_Insights` |
| **관계가 상대 문서 쪽이다** | 4 | 「승격됨 →」 · 「이 기록을 옮긴 것」 |
| **예상이 빗나갔다** | 2 | `Ousterhout TDD 비판` — `diverges_from` 을 기대했는데 아니었다 |

## 예상이 빗나간 둘 — 이것도 답이다

**`Case Study - Ousterhout의 TDD 비판`** 을 `diverges_from` 사례로 뽑았는데 아니었다.
결론이 「Ousterhout의 비판은 순수 TDD에는 **유효하다**. 그러나 현행 SKILL은 ODP 통합
TDD로 그 사정거리 밖에 있다」다. **저자를 딛되 바꾼 게 아니라 비판의 범위 밖임을
보인다.** `contradicts` 도 아니다 — 둘 다 참이다.

**`Heap (힙)` 동음이의 쌍**도 관계가 아니었다. 「같은 이름, 다른 개념」은 어휘 충돌이지
의미 관계가 아니다.

---

# 이 배치가 어휘·계약에 낸 것

라벨 자체보다 이쪽이 값이 컸다.

| 발견 | 결과 |
|---|---|
| 산문 출처가 한 종류가 아니다 | 세 갈래로 갈랐다 — 문서 있음 / 문서 없는 사건 / 갈래만 |
| `source_unknown` 은 Claude 가 못 단다 | 「찾아봤다」는 사람만 할 수 있다 |
| **`informs` 의 방향이 표준과 반대였다** | `informed_by` 로 개명. 「이름은 영어 문법을 따른다」를 원칙으로 |
| `> 원본: [[문서]]` 가 기계적으로 풀린다 | vault 전체 34건 적용 (209 원칙 20 + 다른 type 14) |
| `## 적용 사례` + 선행 Learnings = 원본 | 가이드라인이 그렇게 적으라 했다. 12건 적용 |
| 별칭이 자기참조를 가린다 | 2건. 눈으로는 M-Project 문서로 읽힌다 |
| 사건 문서는 이미 있다 | `Learnings/Incident Response/` 18개. `type` 이 말을 안 할 뿐 |
| `incident ⊂ event` | 원칙을 낳은 것의 70%가 incident 가 아니다 |

# 열어둔 것

### `answered_by` 가 두 표본 모두 0이다

`violates` 와 같은 자리에 설 수 있다. **다만 죽이지 않는다** — C27이 순수 온톨로지
질문 셋 중 하나이고 표본이 3개뿐이다.

관측한 것:

```
By Subquestion 27
   「현재 입장/결론」이 채워짐   13
   대기·보류 표현                4
   판정 불가                    10
```

**답이 채워진 것도 `answered_by` 대상이 없다.** `좋은 생활습관을 유지하기 위해서는`
은 답을 자기 안에 항목으로 누적한다. 밖으로 나가는 링크는 「상세」·「관련」이다.

**`answered_by` 는 「질문 → 답이 있는 다른 문서」를 전제하는데, 실제 구조는 「질문
문서가 답을 담는다」다.** 2차 관찰이나 500 정합화에서 다시 판정한다.

### gold set 표본 선정이 한 번 틀렸다

`창작은 나에게 어떤 의미인가?` 를 「링크 5개 = 답 있음」으로 골랐는데 본문은
**「시기상조 — 아직 Q4 답변을 업데이트할 단계는 아님」**이었다. **답 없는 질문만 둘
골랐다.** 2차 배치에서 답이 채워진 질문을 넣어야 `answered_by` 가 시험된다.

### 문서당 시간을 못 쟀다

준비(문서 읽기·이웃 찾기·후보 뽑기)를 Claude 가 했고 토마토는 판정만 했다.
**실사용 모양과 같으므로 유효한 대리**지만, 시계로 잰 값은 없다.

측정된 것은 이것뿐이다.

```
보류율        0 / 50        중단 기준 30% 통과
자문          5건           전부 어휘·계약의 결함이었다
asserted     전부. proposed 0     ← 파일럿은 77% 가 proposed 였다
```

**`proposed` 가 0인 것이 이 배치의 성과다.** 준비를 Claude 가 하고 근거를 본문에서
찾는 방식으로 바꾸니 위임이 사라졌다.
