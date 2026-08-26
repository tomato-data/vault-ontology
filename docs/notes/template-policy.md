# 템플릿 type·경로 정책 — 조사 결과와 미결

> 2026-08-26 조사. Phase 10의 C24 판정에서 파생됐다.
> **3부 본류가 아니다.** Phase 11 파일럿이 끝난 뒤 한 번에 처리한다.

## 결정된 것

C24에서 **관례 B**를 택했다 — 템플릿은 자기가 만들 문서의 `type`을 달고, 「이건
템플릿이다」는 **경로**로 표시한다.

## 먼저 — 스키마 정본과 충돌한다

`000 Index/Maintenance/Vault 온톨로지 — 스키마 정본.md` 110행:

> **template은 자기가 낳을 문서가 아니다**: `Trade-offs Matrix Template`은
> `tradeoff`가 아니라 `template`이다.

그런데 하루 뒤 **2026-08-11 커밋이 000 Index 9개를 반대로** 바꾸며 적었다:

> 파일 하나에 frontmatter 블록은 하나뿐이라 둘 중 하나만 담을 수 있다.
> 태어날 문서 쪽을 담는다. 템플릿 자신의 정체성은 경로가 말한다.

**vault 안에 규칙이 둘 있고 서로 반대다.** C24는 후자를 택했으므로 정본 110행과
`type` 표의 `template` 행을 함께 고쳐야 한다.

## 진짜 기준은 「템플릿이냐」가 아니었다

| 부류 | 성질 | 해당 |
|---|---|---|
| **통째 복사형** | 플러그인·파일 복사가 frontmatter를 그대로 옮긴다 | 000 Index 9 · Career 5 · 302 둘 |
| **본문 품기형** | 사용법 + 본문 안의 양식. frontmatter가 **안 따라간다** | 499 셋 · AI-Ops 둘 · 209 둘 |

**본문 품기형에 관례 B를 적용하면 `type`이 그 파일 자신을 설명하지 않게 된다.**
`q type decision`에 빈 양식이 섞인다.

## 14개 파일별 제안

| # | 파일 | 제안 `type` | 확신 |
|---|---|---|---|
| 1 | 209/templates/기술 부채 카탈로그 | `reference` (대안 `project-doc`) | 애매 |
| 2 | 209/templates/보류 항목 추적 대장 | `reference` (대안 `project-doc`) | 애매 |
| 3 | AI-Ops/guides/CLAUDE.md 템플릿 (일반) | `procedure` | 애매 · 본문 품기형 |
| 4 | AI-Ops/guides/CLAUDE.md 템플릿 (학습) | `procedure` | 애매 · 본문 품기형 |
| 5 | 302.7/improvements-deepresearch/_template | `project-doc` | **확실** (형제 13개가 전부) |
| 6 | 302.8/adr/0000-template | `project-doc` | 실측 확실 / 의미상 `decision` |
| 7~11 | Career/_Template/ 5개 | `project-doc` | **확실** |
| 12 | 499/Case Study Template | `case` | 확실 · 본문 품기형 |
| 13 | 499/Decision Node Template | `decision` | 중복 해소 선행 |
| 14 | 499/Trade-offs Matrix Template | `tradeoff` | 중복 해소 선행 |

**300 Runtime에 사는 7개는 전부 `project-doc`으로 수렴한다.** 구역 규칙이 세부
의미를 덮기 때문이다. 관례 B가 300 안에서는 정보를 거의 만들지 않는다.

## 중복 2쌍은 판본이 아니라 다른 물건이다

| | `000 Index/Templates/` | `400/499 …/` |
|---|---|---|
| 형태 | 직접 인스턴스화형. 본문이 곧 새 문서 | 가이드 문서형. 양식을 펜스 안에 품음 |
| 줄 수 | 94 · 127 | 176 · 220 |
| mermaid | 진짜 펜스 → 렌더됨 | 풀어 씀 → **복사해도 다이어그램이 안 나온다** |
| 태그 | frontmatter | 양식 안 인라인 → **태그 일원화 규칙 위반을 재생산** |

**499에만 있고 실물이 실제로 쓰는 것:**

```
Forces Analysis     tradeoff 43개 중 18개
실무 적용 기록       decision+tradeoff 86개 중 35개   (가이드라인이 "필수!"로 표기)
```

**껍데기는 000 Index가 옳고 알맹이는 499가 옳다.** `.obsidian/templates.json`이
`000 Index/Templates` 한 곳만 받도록 하드코딩돼 있어 그 폴더는 못 옮긴다.

**제안** — 499의 양식 본문을 000 Index 껍데기에 옮겨 담아 한 파일로 합치고,
499의 바깥 껍데기(사용법·패턴·체크리스트)는 `Logic Forge 가이드라인`으로 흡수한다.
남긴 쪽에 `supersedes`를 적는다. 그러면 `499 Logic Forge Templates/`가 비고
400 대역의 템플릿 문제가 사라진다.

## 파일을 안 옮기고도 되는 것

```python
# 지금 — 14개 중 6개만 잡는다
TEMPLATE_PATH = re.compile(r"(^|/)(Templates|_Template)/|(^|/)_template\.md$")

# 제안 — 14개 전부 + 000 Index 9개 = 23개
TEMPLATE_PATH = re.compile(r"(^|/)_?[Tt]emplates?/|(^|/)(_|\d{4}-)?template\.md$")
```

**커버리지 6/14 → 14/14.** 이동은 그다음에 해도 된다. 지금 그대로 관례 B로 가면
`type` 분기가 0건이 되므로 **경로가 유일한 식별자**가 되는데, 현재 정규식은 23개
중 8개를 놓친다.

## 이동 위험 — 실측

**Obsidian 위키링크 파손은 사실상 0건이다.** 진짜 위험은 경로를 문자열로 박아 둔 곳이다.

| 하드코딩 | 값 | 영향 |
|---|---|---|
| `.obsidian/templates.json` | `000 Index/Templates` | **이 폴더는 못 옮긴다** |
| `.obsidian/daily-notes.json` | `000 Index/Templates/Daily Template` | 같음 |
| `.vault-lint.json` | `skip_frontmatter_in` | 새 경로 추가 필요 |
| `vault.py:674` | `TEMPLATE_PATH` | 위 정규식 |
| `vault.py:187·194` | `ZONE_TYPES`/`SUBDIR_TYPES`의 `template` | 관례 B 후 무의미 |
| `vault.py:737` | `GRAPH_EXCLUDE` | 템플릿이 없어 질의가 오염된다 |

## 기존 버그

`400 Logic Forge/Logic Forge 가이드라인.md` 144~145행이 bare
`[[Decision Node Template]]` · `[[Trade-offs Matrix Template]]`를 쓴다.
**같은 이름 파일이 둘이라 Obsidian이 어디로 갈지 임의로 정한다.** 136~137행은
경로를 지정했는데 그 두 줄만 안 했다. 중복 해소가 끝나야 사라진다.

---

## 사람이 정해야 할 것 7건

1. **`template`을 13값에 남기나?** 관례 B 후 이 값을 쓰는 문서가 0이 된다. 빼면 12값이 되고 스키마 정본·`vault.py:39`·`vault/schema.py:24`를 함께 고쳐야 한다.
2. **본문 품기형(3·4·12·13·14)에 관례 B를 적용하나?** (a) 적용하고 질의에서 경로로 뺀다 (b) 직접 인스턴스화형으로 개조한다 (c) 이 부류만 `procedure`로 둔다.
3. **ADR의 진짜 `type`.** 실물 16개가 `project-doc`인 것은 300 일괄 규칙의 결과지 판정이 아니다. `decision`으로 재판정하면 라우팅 경고 16건이 뜬다.
4. **`공고`는 `project-doc`인가 `source-note`인가.** 같은 폴더의 외부 콘텐츠 둘은 `source-note`인데 `Levit/공고.md` 실물은 `project-doc`이다.
5. **209의 둘을 `reference`로 하면** `SUBDIR_TYPES`에 걸려 경고가 뜬다. 표를 넓히든, 다른 type을 고르든, 209 밖으로 옮기든.
6. **중복 2쌍을 어디에 남기나.** core Templates 플러그인으로 실제로 꽂아 쓰는지에 따라 갈린다.
7. **폴더 이동을 지금 하나?** 정규식만 고치면 이동 없이 14/14가 잡힌다.
