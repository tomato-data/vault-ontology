# vault-cli

Obsidian vault 정합성 도구. **단일 파일, 표준 라이브러리만.**

볼트가 iCloud 위에 있어 의존성을 늘리면 그것도 동기화 대상이 된다. 그래서 `vault.py` 하나로 끝낸다.

```bash
python3 ~/Desktop/Code/vault-cli/vault.py <명령>

# 자주 쓰면 별칭을 만든다
alias vault='python3 ~/Desktop/Code/vault-cli/vault.py'
```

`--vault` 를 생략하면 `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault` 를 쓴다. 명령 앞뒤 어디에 놓아도 된다.

종료 코드: `0` 이상 없음 · `1` 위반 발견 · `2` 사용법 오류.

---

## 명령

| 명령 | 하는 일 |
|---|---|
| `doctor` | 유실·손상 검사. `--restore` 로 git에서 되살린다 |
| `lint` | frontmatter·위키링크 정합 검사 |
| `new` | 스키마를 통과한 문서만 만든다 |
| `ingest` | 이미 쓴 초안을 볼트로 편입한다 |
| `template` | 스키마 뼈대 출력 / `--list` 로 볼트의 양식 나열 |
| `build` | 그래프를 SQLite로 뽑는다 |
| `q` | 그래프 질의 |
| `install-hook` | pre-commit 훅 설치 (한 번) |

---

## 설계 불변식

**생성과 검사가 코드를 공유한다.**

```
vault new   → 검증 통과한 문서만 생성
vault lint  → 검증 실패한 문서 검출
                  ↑ 같은 validate_frontmatter()
```

따로 만들면 반드시 어긋난다. 공유하면 *만든 것은 반드시 검사를 통과한다* 가 구조적으로 보장된다.

**거부지 경고가 아니다.** 경고로 두면 무시된다 — hex 태그를 v2.37에서 청소하고도 다시 쌓인 것이 증거다. 예외는 라우팅(`--dir` vs `--type`) 하나뿐이다. 디렉토리와 타입의 대응이 완전하지 않기 때문이다.

**파생 가능한 사실은 저장하지 않는다.** `part_of` 는 디렉토리에서 빌드 시점에 유도한다. `.vault-graph.db` 는 gitignore — 언제든 다시 만든다.

스키마의 단일 출처는 볼트의 `100 Private Log/199 Private Kernel/Vault 온톨로지 — 스키마 정본.md` 다. `vault.py` 의 `TYPES`·`SUMMARY_MAX`·`BUILDS_ON_MAX` 를 고치면 그 문서도 같이 고친다.

---

## doctor — 유실 감지

```bash
vault doctor              # 검사
vault doctor --restore    # 사라진 파일을 git에서 되살린다
```

| 검사 | 무엇을 보나 | 놓쳤던 사고 |
|---|---|---|
| `missing` | `git ls-files --deleted` | 커밋 `e6d3261a` — `.md` 23건 삭제 |
| `shrunk` | HEAD 대비 줄 수가 절반 아래 | 커밋 `d892cbc0` — VPN 본문 44줄 소실 |
| `icloud` | `.icloud` 플레이스홀더 | evict 진행 중 |

### 왜 만들었나

2026-08-10, 커밋 하나에 `.md` 23건 삭제가 함께 기록돼 있었다. 11건은 대체 문서 없는 유실이었고, `Python - Uvicorn vs Gunicorn 워커 관리 완전 가이드`(2,013줄)는 다른 문서 14곳이 여전히 링크하고 있었다.

같은 파일들이 3·4·6·7·8월 커밋 8개에서 반복 삭제됐다. iCloud가 파일을 놓쳤다 되찾는 패턴이다. 사람은 이걸 못 본다 — 커밋 메시지가 날짜 한 줄이고 `git add -A` 로 한 번에 올리기 때문이다.

별개로 2026-03-07에는 `05. VPN.md` 의 본문 44줄이 지워지고 그 자리에 챕터 목차가 들어갔다. **삭제가 아니라 수정이라 ` M` 으로만 떴다** — `shrunk` 검사가 있는 이유다.

### pre-commit 훅

```bash
vault install-hook
```

삭제나 내용 급감이 스테이지에 올라온 커밋을 **거부한다.**

```
커밋을 멈춘다. 의도하지 않은 유실로 보인다.

  삭제 1건
    600 Content Observatory/601 Books/개발/SQL Cookbook/…

  내용 급감 1건
       711 → 312  줄  싱글톤 vs 팩토리 패턴…
```

의도한 삭제는 두 가지로 통과시킨다.

```bash
VAULT_ALLOW_DELETE=1 git commit -m "..."   # 권장. 의도를 남긴다
git commit --no-verify -m "..."            # 훅 전체를 건너뛴다
```

> **훅은 이 Mac에만 있다.** `.git/hooks/` 는 git이 추적하지 않는다. 다른 Mac에서는 `install-hook` 을 다시 돌린다.

> **evict된 파일은 `--restore` 로 덮지 마라.** 먼저 `brctl download <경로>` 로 내려받는다. 클라우드 쪽이 더 최신이면 그걸 잃는다. `doctor` 가 `.icloud` 를 먼저 보고하는 이유다.

---

## lint — 정합 검사

```bash
vault lint                     # 둘 다
vault lint --links             # 링크만
vault lint --frontmatter       # frontmatter만
vault lint --all               # 제외 규칙 없이 전부
vault lint -v --limit 50       # 위반을 하나씩
vault lint --json out.json     # 결과 저장
```

검사하는 것: `type` 13값 · `summary` 80자 · `created` 실제 날짜 · `builds_on` 해결·3개 이하 · 의도치 않은 태그 · 위키링크 해결.

### 제외 규칙

볼트 루트의 `.vault-lint.json` 이 정한다. 없으면 코드의 기본값을 쓴다. **이 파일은 커밋한다** — 무엇을 왜 뺐는지가 감사 대상이다.

```json
{
  "sources": ["300 Runtime/301 Day Notes", "800 TRPG", "900 Archive"],
  "targets": ["...", "참조", "파일명"],
  "files":   ["000 Index/Templates/Daily Template.md", "…"]
}
```

- `sources` — 여기서 나온 깨진 링크는 **고칠 오류가 아니라 당시를 가리키는 흔적**이다. Day Note가 끝난 일의 계획서를 링크하는 건 자연스럽다.
- `targets` — 템플릿 자리표시자.
- `files` — 파일 통째 제외. 적어두고 아직 안 쓴 목록, 깨진 링크를 나열하는 게 일인 감사 문서, 플러그인이 복사하는 템플릿.

스킬 이름(`monthly-elevate`, `rails-domain-patterns/SKILL`)은 설정 없이 자동으로 뺀다. `~/.claude/skills/` 와 볼트의 `.claude/skills/` 를 읽는다.

### 파서에서 조심한 것

이 자리에서 네 번 잘못 셌다. 고친 내용을 남긴다.

| 함정 | 증상 | 처리 |
|---|---|---|
| 표 안의 `\|` | `[[문서\|별칭]]` 타깃 끝에 역슬래시가 남는다 | `\\|` 를 먼저 자른다 |
| `splitext` | `No.013 현자의 돌` → `No` + `.013 현자의 돌` | `.md` 만 명시적으로 뗀다 |
| 대소문자 | macOS는 `python` 과 `Python` 을 구분하지 않는다 | 케이스 무시 충돌을 따로 본다 |
| frontmatter 중복 | `builds_on` 이 링크 검사에도 잡혀 두 번 센다 | 링크는 본문만 본다 |
| `\s*(.+)$` | `\s` 가 개행을 먹어 빈 `summary:` 가 다음 줄을 읽는다 | `[ \t]*` 로 좁힌다 |
| `2026-13-99` | 형태는 맞는데 없는 날짜다 | `date.fromisoformat` |

태그 검출도 네 번 고쳤다. 이 넷은 태그가 아니다.

```
[EC2](#ec2-elastic-…)   마크다운 링크 목적지
https://…#_oidc         URL 조각
#Stack/Python           사람이 다는 계층 태그
#729651                 순수 숫자 — Obsidian은 태그로 만들지 않는다
```

태그만 있는 줄은 통째로 사람의 태그 줄로 본다. 태그는 유저가 직접 단다.

---

## new / ingest / template — 생성 관문

```bash
vault new --type concept --title "CIDR 계산" \
  --dir "200 Dev Knowledge Base/203 Backend/Network" \
  --summary "서브넷 마스크로 호스트 수를 세는 법" \
  --builds-on "[[네트워크 계층]]" <<'EOF'
# CIDR 계산
…
EOF

vault ingest /tmp/draft.md --dir "…" --summary "…" --rm
vault template --type case      # 뼈대 출력
vault template --list           # 볼트의 양식 문서 나열
```

거부하면 **파일이 아예 안 생긴다.** 조건은 스키마 정본의 표와 같고, 여기에 실측으로 얻은 셋을 더했다.

| 조건 | 왜 |
|---|---|
| 파일명에 백틱·대괄호·파이프 | `` `-i` 인자에 대해서.md `` 가 링크 파서를 헷갈리게 했다 |
| 같은 파일명이 볼트에 이미 있음 | `Hub`·`Worklog` 중복이 링크 대상을 못 고르게 만들었다 |
| 본문이 빔 | |

태그 인자는 없다.

`ingest` 는 초안의 도메인 필드를 살린다. `tags:` 처럼 값이 다음 줄에 오는 블록을 한 덩어리로 유지한다 — 키 줄만 뽑으면 리스트가 뭉개져 YAML이 깨진다. YAML 키에 공백이 있는 것(`Read Status:`)도 챙긴다.

### 템플릿의 frontmatter

Obsidian 플러그인은 템플릿 파일을 **통째로 복사**한다. 그래서 `000 Index/Templates/` 의 템플릿은 자기 정체성(`type: template`)이 아니라 **태어날 문서의 frontmatter** 를 담는다.

```yaml
# Daily Template.md
---
type: log
summary:
created: {{date:YYYY-MM-DD}}
---
```

이들은 `type: template` 이 아니므로 `template --list` 가 경로로도 찾는다. `.vault-lint.json` 의 `files` 에도 넣는다.

`400 Logic Forge` 쪽 템플릿은 「사용법 + `## 템플릿`」 구조로 본문 안에 양식을 두므로 이 문제가 없다. 그쪽은 `type: template` 을 유지한다.

---

## build / q — 그래프

```bash
vault build                      # .vault-graph.db 생성

vault q path "문서 이름"          # builds_on 이행 폐쇄 = 학습 경로
vault q near "문서 이름"          # 링크·역링크·같은 태그 이웃
vault q orphans [구역]            # 인바운드 0
vault q type concept
vault q tag Stack/Python
vault q stats
vault q sql "SELECT …"           # 날것
```

| 테이블 | 내용 |
|---|---|
| `node` | path · name · zone · dir · type · summary · created · bytes |
| `edge` | `builds_on`·`supersedes` (frontmatter) / `links_to`·`part_of` (유도) |
| `tag` | 슬래시가 있는 계층 태그만 |

### 실측 (2026-08-11)

```
노드 3,919 · 엣지 12,266 · 태그 2,820
  links_to 10,702 · part_of 1,174 · builds_on 387 · supersedes 3

빌드 0.8초 · 질의 40ms
```

**상주 서버가 필요 없다.** `builds_on` 사슬 깊이는 최대 7이라 이행 폐쇄가 실제로 여러 단을 탄다.

### 800 TRPG 를 빼는 이유

같은 `type:` 키를 **다른 뜻으로** 쓴다.

```
TRPG의 type:  완제품 1041 · 원재료 351 · 중간재 317 · 마물 101 · 마족 12
```

게임 아이템 분류다. 섞으면 type 축이 깨진다. `900 Archive`·`.claude`·`CLAUDE.md` 도 뺀다.

빼도 링크는 그쪽을 가리킨다. 그래서 해석 실패를 두 줄로 나눠 보고한다 — 제외 구역을 가리키는 것(정상)과 그 밖(`lint --links` 가 분류).

---

## 다른 Mac에 놓을 때

```bash
git clone <이 저장소> ~/Desktop/Code/vault-cli
python3 ~/Desktop/Code/vault-cli/vault.py install-hook
```

훅은 추적되지 않으므로 Mac마다 설치한다. `.vault-lint.json` 은 볼트에 있으니 따라온다. `.vault-graph.db` 는 `vault build` 로 만든다.

---

## 앞으로

v1 은 Python + rdflib/owlrl 로 추론을 붙이고, v2 는 Rust + Oxigraph 로 옮긴다.

**판단 기준은 하나다** — 재귀 CTE로 부족해서 SPARQL property path(`:builds_on+`)나 추론이 필요해지는가. 2주 써보고 정한다. 지금은 아니다.

사람 경로(Obsidian `Ctrl+N`)는 아직 열려 있다. Templater 연결이 남은 조각이다.
