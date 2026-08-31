# gold set 50 — 매니페스트

> Phase 12 Step 3 산출물. 2026-08-31 확정.
> **Step 4가 이 목록을 손으로 라벨링한다.** 그것이 곧 문서당 비용의 측정이다.

## 배분

`phase12.md` Step 3의 최소 대역 분포에, 「700·600에서 뺀 자리는 400·200으로」를 적용했다.

```
000    3      100    6      200   12      300    8
400   10      500    6      600    4      900    1
                                         ────
                                          50
```

- **700 Life Stack — 0.** 실측이 「판단이 아니라 사전」이라 했다 (`reference` 111 · 밖으로 나가는 링크 8개).
- **900 Archive — 1.** D3가 「질문이 지목한 문서만」이라 했고, **C17(종결된 질문의 결론)이 지목한다.**
- **601 Books 챕터 필사 914개 — 제외.** 저자의 말이지 내 주장이 아니다. 대표 노트만 들어온다.
- **800 TRPG — 제외.** `type:`을 게임 아이템 분류로 쓴다. 같은 키 다른 뜻.

## type 분포

```
reflection     12
concept        8
principle      6
project-doc    6
decision       6
procedure      2
log            2
tradeoff       2
review         2
source-note    2
case           1
—              1
```


## 000 Index — 3

| | `type` | 문서 | 왜 뽑았나 |
|---|---|---|---|
| 1 | `principle` | `000 Index/Maintenance/디렉토리 철학/400 Logic Forge.md` | 메타 원칙. 「필드가 없어서가 아니라 안 채운 것」 |
| 2 | `procedure` | `000 Index/Maintenance/가이드라인/209 Principles 가이드라인.md` | C04 가 요구하는 규칙의 원본 |
| 3 | `concept` | `000 Index/Dots/0429_tdd_plan_go_post_e2e_분석.md` | 패턴 7항목 — 섹션 앵커 대상 |

## 100 Private Log — 6

| | `type` | 문서 | 왜 뽑았나 |
|---|---|---|---|
| 1 | `reflection` | `100 Private Log/103 Debugger/103.1 self/모든 정답은 일시적이다.md` | 파일럿 10번. expresses · 대상이 항목 |
| 2 | `reflection` | `100 Private Log/103 Debugger/103.1 self/이방인의 뫼르소와 나.md` | 600 ↔ 100 교차 |
| 3 | `reflection` | `100 Private Log/103 Debugger/103.1 self/2026-05-20 본질주의와 우월감 회로 자기 점검.md` | 같은 경험의 재해석 |
| 4 | `reflection` | `100 Private Log/103 Debugger/103.4 stack/BNV 솔루션.md` | 개인 가치가 커리어 판단에 |
| 5 | `reflection` | `100 Private Log/104 Affinity/책.md` | 600 과 짝 |
| 6 | `reflection` | `100 Private Log/104 Affinity/영상.md` | 600 과 짝 |

## 200 Dev Knowledge Base — 12

| | `type` | 문서 | 왜 뽑았나 |
|---|---|---|---|
| 1 | `principle` | `200 Dev Knowledge Base/209 Principles/Backend/FastAPI 테스트에서 TestClient를 with로 감싸지 마라.md` | 원본 있음 — derived_from 명시 |
| 2 | `principle` | `200 Dev Knowledge Base/209 Principles/Backend/JWT 기반 다중 로그인 제한 패턴.md` | 원본 있음 |
| 3 | `principle` | `200 Dev Knowledge Base/209 Principles/Backend/DB Connection Pool은 85%까지만, 나머지는 headroom.md` | 원본 없음 — source_unknown 후보 |
| 4 | `principle` | `200 Dev Knowledge Base/209 Principles/Backend/IO-bound 서비스는 asyncio를 우선하라.md` | 원본 없음 |
| 5 | `concept` | `200 Dev Knowledge Base/205 DB/Stacks/PostgreSQL/PostgreSQL 스키마 설계 전략 (public 비우기, 커스텀 스키마 활용).md` | supersedes 실물 |
| 6 | `concept` | `200 Dev Knowledge Base/207 DevOps/Ansible/Ansible 인벤토리 — 호스트 그룹과 -i 옵션.md` | supersedes 2건 |
| 7 | `concept` | `200 Dev Knowledge Base/207 DevOps/AWS/Cost Optimization/08 FinOps 실천 — 가시화·약정 관리·자동화.md` | 600 을 builds_on — 대역 교차 |
| 8 | `concept` | `200 Dev Knowledge Base/201 CS Foundations/Data Structures/Heap (힙) — 자료구조.md` | 동음이의 쌍 |
| 9 | `concept` | `200 Dev Knowledge Base/201 CS Foundations/Data Structures/Heap (힙) — 메모리 영역.md` | 동음이의 쌍 |
| 10 | `concept` | `200 Dev Knowledge Base/203 Backend/Concurrency/Race Condition.md` | 사례 4항목 |
| 11 | `principle` | `200 Dev Knowledge Base/209 Principles/_개발 규율집 (Project Discipline Bible).md` | 원칙 묶음 |
| 12 | `procedure` | `200 Dev Knowledge Base/202 Languages/Python/FastAPI/Basics/FastAPI - Swagger UI에서 Bearer 토큰 사용하기.md` | procedure 대조군 |

## 300 Runtime — 8

| | `type` | 문서 | 왜 뽑았나 |
|---|---|---|---|
| 1 | `project-doc` | `300 Runtime/302 BNV Solutions/302.7 E-Project/302.7.4. Learnings/System Architecture/회계 데이터 무결성 4계층 — append-only ledger·마감·provenance·reconciliation.md` | 원칙을 어긴 기록 |
| 2 | `project-doc` | `300 Runtime/302 BNV Solutions/302.7 E-Project/302.7.4. Learnings/Code Architecture/API 레이어 정리와 헬퍼 중앙화.md` | 규칙 위반 47건 — 수동 5건 |
| 3 | `project-doc` | `300 Runtime/302 BNV Solutions/302.8 duoacademy/302.8.4. Learnings/Code Architecture/테스트 스위트 성능 — 측정 우선, 루프≠게이트, 검사량 축소.md` | 파일럿 4번. applies 2 |
| 4 | `project-doc` | `300 Runtime/302 BNV Solutions/302.5 bnvsglobal/302.5.4. Learnings/Domain/bnvsglobal 인프라 진화.md` | elevate verdict: promoted |
| 5 | `project-doc` | `300 Runtime/302 BNV Solutions/302.7 E-Project/302.7.4. Learnings/Code Architecture/Best Practices 감사 및 개선 (2026-04).md` | elevate verdict: skip |
| 6 | `log` | `300 Runtime/301 Day Notes/2026-08-26.md` | Day Note — 관계를 안 붙이는 대조군 |
| 7 | `log` | `300 Runtime/320 Career/320.4. Applications/Levit/커피챗 기록 — 레브잇 2026-08.md` | log · 최근 |
| 8 | `project-doc` | `300 Runtime/320 Career/320.7. Blog/A. 실무 사건 — 겪은 일/01 post — 콘솔에서 IaC까지.md` | 경험 → 글 |

## 400 Logic Forge — 10

| | `type` | 문서 | 왜 뽑았나 |
|---|---|---|---|
| 1 | `decision` | `400 Logic Forge/401 Architecture Playbook/Layer 2. Backend/Architecture Style Selection/Decision Node - Architecture Style Selection.md` | 충돌 A — 팀 10명 임계 |
| 2 | `decision` | `400 Logic Forge/401 Architecture Playbook/Layer 2. Backend/Code-Structure/Decision Node - Pragmatic vs Clean Architecture.md` | 충돌 B — 팀 5명 · Source 있음 |
| 3 | `tradeoff` | `400 Logic Forge/401 Architecture Playbook/Layer 2. Backend/Code-Structure/Trade-offs - Pragmatic vs Clean Architecture.md` | 그 짝 |
| 4 | `concept` | `400 Logic Forge/403 Case Studies/Case Study - Ousterhout의 TDD 비판과 ODP 통합 TDD의 대응.md` | diverges_from — 저자를 딛되 바꿨다 |
| 5 | `case` | `400 Logic Forge/403 Case Studies/Case Study - 테스트 DB 프로비저닝 (testcontainers 병목).md` | builds_on 실물 |
| 6 | `decision` | `400 Logic Forge/401 Architecture Playbook/Layer 3. Application/Authentication/Decision Node - JWT vs Session.md` | Source + Trade-offs 갖춤 |
| 7 | `decision` | `400 Logic Forge/401 Architecture Playbook/Layer 2. Backend/Task-Queue/Decision Node - Live Activity 종료 폴링 전략.md` | Source + Trade-offs 갖춤 |
| 8 | `decision` | `400 Logic Forge/401 Architecture Playbook/Layer 2. Backend/Server Architecture/Decision Node - 저사양 vCPU 환경의 ASGI 서버 구성.md` | Source + Trade-offs 갖춤 |
| 9 | `tradeoff` | `400 Logic Forge/401 Architecture Playbook/Layer 3. Application/Architecture-Style/Trade-offs - Pragmatic vs Clean Architecture.md` | 같은 이름 다른 문서 — Layer 3 |
| 10 | `decision` | `400 Logic Forge/401 Architecture Playbook/Layer 3. Application/Architecture-Style/Decision Node - Pragmatic vs Clean Architecture.md` | 같은 이름 다른 문서 — Layer 3 |

## 500 Mind Compiler — 6

| | `type` | 문서 | 왜 뽑았나 |
|---|---|---|---|
| 1 | `reflection` | `500 Mind Compiler/Q1. Better Developer/_Insights.md` | 19항목 — 섹션 앵커 |
| 2 | `reflection` | `500 Mind Compiler/Q7. Who Am I/_Patterns.md` | C08 — 믿음의 시간 변화 |
| 3 | `reflection` | `500 Mind Compiler/Q7. Who Am I/_Insights.md` | 24항목 |
| 4 | `reflection` | `500 Mind Compiler/Q4. Enriching Life/By Subquestion/창작은 나에게 어떤 의미인가?.md` | answered_by 있음 (링크 5) |
| 5 | `reflection` | `500 Mind Compiler/Q6. Relationship/By Subquestion/좋은 친구란 무엇인가?.md` | 답 없음 — 탐구 대기 |
| 6 | `reflection` | `500 Mind Compiler/_Compile Log/Quarterly Synthesis - 2026-Q1.md` | 인사이트 35회 참조 |

## 600 Content Observatory — 4

| | `type` | 문서 | 왜 뽑았나 |
|---|---|---|---|
| 1 | `review` | `600 Content Observatory/602 Frames/영화/기생충.md` | review — 새 type 의 첫 gold |
| 2 | `review` | `600 Content Observatory/603 Game/Valheim.md` | review — 게임 대표 노트 |
| 3 | `source-note` | `600 Content Observatory/604 YouTube/개발/The Passionate Programmer/3. Abstract Factory — Strategy에 일관성을 부여하는 패턴.md` | source-note — 화자의 주장 |
| 4 | `source-note` | `600 Content Observatory/601 Books/개발/AWS 비용 최적화 바이블/KAO 방법론.md` | source-note — 08 FinOps 와 쌍 |

## 900 Archive — 1

| | `type` | 문서 | 왜 뽑았나 |
|---|---|---|---|
| 1 | `—` | `900 Archive/Mind Compiler/_Insights.md` | C17 지목 · frontmatter 없음 |

---

## 난점 커버리지 — 일부러 넣은 것

`phase12.md`가 「쉬운 문서만 고르지 않는다」며 나열한 난점 10가지다.

| 난점 | 어느 문서가 담나 |
|---|---|
| 한 문서에 여러 주장 | `Q1 _Insights`(19) · `Q7 _Insights`(24) · `Q7 _Patterns` · `Race Condition`(사례 4) |
| **서로 충돌하는 문서** | `Architecture Style Selection`(팀 10명) ↔ `Pragmatic vs Clean`(팀 5명) |
| **같은 이름 다른 문서** | `Pragmatic vs Clean` 이 Layer 2·Layer 3에 각각. Trade-offs 도 마찬가지 |
| `supersedes` 관계 | `PostgreSQL 스키마 설계 전략` · `Ansible 인벤토리`(2건) |
| 근거가 불명확한 원칙 | `DB Connection Pool 85%` · `IO-bound asyncio` — 209의 46개 중 둘 |
| 문서 이동·이름 변경 이력 | `900 Archive/Mind Compiler/_Insights` — 경로가 바뀌었고 결론은 살아 있다 |
| 같은 개념 다른 용어 | `Heap (힙) — 자료구조` ↔ `Heap (힙) — 메모리 영역` (동음이의) |
| 한국어·영어 혼재 | `Best Practices 감사 및 개선` · `Abstract Factory — Strategy에…` |
| 같은 경험을 다르게 해석 | `2026-05-20 본질주의와 우월감 회로 자기 점검` · `Q7 _Patterns` |
| 개인 가치가 개발·커리어 결정에 | `BNV 솔루션` · `01 post — 콘솔에서 IaC까지` |
| 기술 원칙과 삶의 철학의 긴장 | `Ousterhout의 TDD 비판` · `_개발 규율집` |

### 그 밖에 일부러 넣은 것

| | 왜 |
|---|---|
| `기생충` · `Valheim` | **`review` 는 2026-08-26에 생긴 type 이다.** 첫 gold 사례가 필요하다 |
| `KAO 방법론` + `08 FinOps 실천` | **대역 교차의 실물.** 600 을 200 이 `builds_on` 한다 |
| `좋은 친구란 무엇인가?` | **답이 없는 질문.** C27 의 흥미로운 절반 |
| `2026-08-26` Day Note | **관계를 안 붙이는 대조군.** 「안 붙였다」도 데이터다 |
| `bnvsglobal 인프라 진화` · `Best Practices 감사 및 개선` | `elevate: verdict` 가 `promoted` / `skip` 인 한 쌍 |

---

## Step 4 — 관문을 둔다

**50개를 한 번에 하지 않는다.** `phase11.md`의 두 완료 조건(문서당 시간 · 재라벨링
일치율)이 아직 비어 있고, **Step 4가 그것을 재는 자리**이기 때문이다.

```
1차   앞의 10개를 스톱워치를 들고 라벨링한다
      → 문서당 시간 · 보류율 · 「둘 다 말이 된다」 빈도

      관문 ─────────────────────────────────
      문서당 15분 초과       → 어휘를 좁히거나 의미 단위를 거칠게
      보류 30% 초과          → 같은 조치
      둘 다 통과             → 나머지 40개

2차   나머지 40개
3차   일정 간격 뒤 10개 이상을 다시 라벨링 (혼자)
      → 일치율. 60% 미만이면 어휘를 좁힌다
```

**1차 10개는 대역을 흩어서 고른다.** 한 대역에 몰면 그 대역의 난이도가 전체 비용으로
읽힌다.

```
000  1     디렉토리 철학/400 Logic Forge
100  1     모든 정답은 일시적이다
200  3     FastAPI TestClient · DB Connection Pool 85% · 08 FinOps 실천
300  2     테스트 스위트 성능 · 회계 데이터 무결성 4계층
400  2     Pragmatic vs Clean (Layer 2) · Ousterhout의 TDD 비판
500  1     Q1 Better Developer/_Insights
```

`08 FinOps`와 `Q1 _Insights`를 1차에 넣은 이유가 있다 — **대역 교차와 섹션 앵커가
가장 비쌀 후보**라서, 비용의 상한을 먼저 본다.

---

## 라벨링할 때 각 문서에서 확정하는 것

`phase12.md` Step 4 그대로다.

```
artifact 와 knowledge entity 의 ID          → wikilink. 49개 문서는 경로 포함
표현된 주장·사건·결정·원칙·절차
관계와 정확한 근거 위치                       → 본문 어디를 보고 그렇게 판단했나
assertion 상태                              asserted / proposed
기대되는 SHACL 위반                          Phase 16 이 검사할 것
기대되는 추론과 질의 답                        Phase 18 의 gold answer
```

**「위임」은 승인이 아니다.** 「적절한 걸로 해놓아주세요」는 `proposed:` 다.
파일럿에서 소급 분류하니 **asserted 11 · proposed 37(77%)** 이었다.
