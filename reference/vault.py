#!/usr/bin/env python3
"""vault — Obsidian vault 정합성 도구.

v0-a: 유실 감지 (doctor) + 정합 검사 (lint)
표준 라이브러리만 쓴다. 볼트가 iCloud 위에 있어 의존성을 늘리면 그것도 동기화 대상이 된다.
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

DEFAULT_VAULT = Path.home() / (
    "Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault"
)

# 내용이 이 비율 아래로 줄면 덮어쓰기 사고로 본다.
SHRINK_RATIO = 0.5
# 이 줄 수 미만인 파일은 비율 판정이 무의미해서 건너뛴다.
SHRINK_MIN_LINES = 10


def nfc(s):
    return unicodedata.normalize("NFC", s)


# ── 스키마 ────────────────────────────────────────────────────────────────
# 정본: 볼트의 `100 Private Log/199 Private Kernel/Vault 온톨로지 — 스키마 정본.md`
# 여기를 고치면 그 문서도 같이 고친다.

TYPES = {
    "concept", "procedure", "principle", "decision", "tradeoff", "case",
    "capture", "reflection", "project-doc", "reference", "log", "hub",
    "template",
}
SUMMARY_MAX = 80
BUILDS_ON_MAX = 3
# 본문에서 `#` 뒤에 바로 붙은 문자열을 Obsidian이 태그로 만든다.
# hex 색상(`#6B4E8C`)과 작업 번호(`#15a`)가 대표적인 오염원이다.
#
# 두 가지는 태그가 아니므로 건드리지 않는다.
#   순수 숫자   `#729651` — Obsidian은 숫자만으로 된 태그를 만들지 않는다
#   앵커 링크   `[EC2](#ec2-elastic-compute-cloud)` — 마크다운 링크의 목적지
#   태그 체계   `#Stack/Python` — 사람이 직접 다는 계층 태그
JUNK_TAG = re.compile(
    r"(?<![\w`\\])#(?=\w*[a-zA-Z])[0-9a-zA-Z_-]{2,}(?![0-9a-zA-Z_/-])"
)


def find_junk_tags(body):
    """의도치 않게 태그가 되는 `#...` 를 찾는다.

    사람이 직접 단 태그는 건드리지 않는다 (CLAUDE.md 규칙 #3).
    태그만 있는 줄은 통째로 사람의 태그 줄로 본다.
    """
    out = []
    for line in body.split("\n"):
        # 마크다운 링크 목적지 `](#...)` 와 URL 조각 `…#_oidc` 는 태그가 아니다.
        s = re.sub(r"\]\([^)]*\)", "]()", line)
        s = re.sub(r"https?://\S+", "", s)
        hits = list(JUNK_TAG.finditer(s))
        if not hits:
            continue
        # 이 줄에서 `#...` 을 전부 빼고 남는 게 없으면 사람이 단 태그 줄이다.
        if not re.sub(r"#[0-9a-zA-Z_/-]+", "", s).strip():
            continue
        out += [m.group(0) for m in hits]
    return out


# ── 위키링크 ──────────────────────────────────────────────────────────────

FENCE = re.compile(r"^(```|~~~)")
INLINE_CODE = re.compile(r"`[^`\n]*`")
LINK = re.compile(r"(?<!\\)\[\[([^\[\]\n]+?)\]\]")


def strip_code(text):
    """펜스 코드블록을 줄 단위로 비우고 인라인 코드를 지운다."""
    out, in_fence, marker = [], False, None
    for line in text.split("\n"):
        m = FENCE.match(line.strip())
        if m:
            if not in_fence:
                in_fence, marker = True, m.group(1)
            elif line.strip().startswith(marker):
                in_fence, marker = False, None
            out.append("")
            continue
        out.append("" if in_fence else INLINE_CODE.sub("", line))
    return "\n".join(out)


def link_target(raw):
    """`[[...]]` 안쪽 → 타깃 경로.

    표 안에서는 파이프가 `\\|` 로 이스케이프된다. 그걸 먼저 자르지 않으면
    타깃 끝에 역슬래시가 남아 멀쩡한 링크를 깨진 것으로 센다.
    """
    s = raw.split("\\|")[0].split("|")[0].split("#")[0].split("^")[0]
    return nfc(s.rstrip("\\").strip())


def scan_vault(vault):
    """(md 상대경로 목록, 링크로 쓸 수 있는 이름 -> [상대경로], 전체 상대경로 집합)

    splitext 로 확장자를 떼면 안 된다. `No.013 현자의 돌` 을
    `No` + `.013 현자의 돌` 로 쪼갠다. `.md` 만 명시적으로 뗀다.
    """
    files, index, paths = [], {}, set()
    for root, dirs, fs in os.walk(vault):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in fs:
            rel = nfc(os.path.relpath(os.path.join(root, f), vault))
            paths.add(rel)
            name = nfc(f)
            index.setdefault(name, []).append(rel)
            if name.endswith(".md"):
                index.setdefault(name[:-3], []).append(rel)
                files.append(rel)
    return files, index, paths


def resolve_link(t, index, paths):
    if t in index:
        return True
    if "/" not in t:
        return False
    if t in paths or t + ".md" in paths:
        return True
    needle = "/" + t
    return any(p.endswith(needle) or p.endswith(needle + ".md") for p in paths)


# ── 검사에서 뺄 것 ────────────────────────────────────────────────────────

DEFAULT_IGNORE = {
    # 여기서 나온 깨진 링크는 「고칠 오류」가 아니라 「당시를 가리키는 흔적」이다.
    "sources": [
        "300 Runtime/301 Day Notes",
        "100 Private Log/102 Monthly Diary",
        "800 TRPG", "900 Archive", ".claude", ".trash",
    ],
    # 템플릿 문법·자리표시자
    "targets": ["...", "참조", "파일명", "제목", "경로", "예시"],
    # 적어두고 아직 안 쓴 목록. 미해결 링크가 「만들 것」 표시로 기능한다
    "files": [],
}
CONFIG_NAME = ".vault-lint.json"


def load_ignore(vault):
    cfg = Path(vault) / CONFIG_NAME
    if not cfg.exists():
        return dict(DEFAULT_IGNORE)
    user = json.loads(cfg.read_text(encoding="utf-8"))
    return {k: user.get(k, DEFAULT_IGNORE[k]) for k in DEFAULT_IGNORE}


PLACEHOLDER = re.compile(r"^(\{.*\}|\$\{.*\}|<.*>|.*\b(NN|XXX?|TODO|TBD)\b.*)$", re.I)


def skill_names(vault):
    """볼트 밖에 실재하는 스킬. 링크가 깨져 보여도 정상이다."""
    names = set()
    for base in (Path.home() / ".claude" / "skills", Path(vault) / ".claude" / "skills"):
        if base.is_dir():
            names |= {nfc(d.name) for d in base.iterdir() if not d.name.startswith(".")}
    return names


# ── 라우팅 (2단계) ────────────────────────────────────────────────────────
# `--dir` 이 `--type` 과 모순되면 경고한다. 거부가 아니다 —
# 디렉토리와 타입의 대응이 완전하지 않다. case는 200에도 300에도 갈 수 있다.
#
# 값은 볼트의 실제 분포로 뽑았다 (2026-08-11).
#   500 Mind Compiler     reflection 94 / 95
#   600 Content Observatory  capture 1248 · hub 144 / 1393
#   300 Runtime           project-doc 712 · log 334 / 1055
ZONE_TYPES = {
    "100 Private Log": {"log", "reflection", "reference", "principle"},
    "300 Runtime": {"project-doc", "log", "template", "case", "procedure"},
    "400 Logic Forge": {"tradeoff", "decision", "hub", "case", "template", "procedure"},
    "500 Mind Compiler": {"reflection", "hub", "procedure"},
    "600 Content Observatory": {"capture", "hub", "procedure"},
}
# 구역 안의 특정 디렉토리는 더 좁다.
SUBDIR_TYPES = {
    "200 Dev Knowledge Base/209 Principles": {"principle", "template", "hub"},
    "300 Runtime/301 Day Notes": {"log"},
    "100 Private Log/102 Monthly Diary": {"log"},
}


def routing_warning(rel, t):
    """경로와 type이 어긋나면 한 줄 경고. 맞으면 None."""
    for prefix, ok in SUBDIR_TYPES.items():
        if rel.startswith(prefix + "/"):
            return None if t in ok else (
                f"{prefix} 는 보통 {'·'.join(sorted(ok))} 다. `{t}` 가 맞나")
    zone = rel.split("/")[0]
    ok = ZONE_TYPES.get(zone)
    if ok and t not in ok:
        return f"{zone} 는 보통 {'·'.join(sorted(ok))} 다. `{t}` 가 맞나"
    return None


# 파일명에 쓰면 안 되는 것.
# 백틱은 링크 파서를 헷갈리게 한다 (`` `-i` 인자에 대해서.md `` 가 그랬다).
BAD_NAME = re.compile(r"[`\[\]|#^\\/:*?\"<>]")


def is_skill_ref(t, skills):
    """`monthly-elevate` 도, `rails-domain-patterns/SKILL` 도 스킬 참조다."""
    t = nfc(t)
    if t in skills:
        return True
    head = t.split("/")[0]
    return head in skills and t.split("/")[-1].upper().startswith("SKILL")


class Git:
    def __init__(self, root):
        self.root = str(root)

    def _run(self, *args, binary=False):
        r = subprocess.run(
            ["git", "-C", self.root, "-c", "core.quotepath=off", *args],
            capture_output=True,
        )
        if r.returncode != 0 and not binary:
            return ""
        return r.stdout if binary else r.stdout.decode("utf-8", "replace")

    def lines(self, *args):
        return [l for l in self._run(*args).splitlines() if l]

    def show(self, rev, path):
        """rev 시점의 파일 내용. 없으면 None."""
        r = subprocess.run(
            ["git", "-C", self.root, "show", f"{rev}:{path}"], capture_output=True
        )
        return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None


def check_missing(g):
    """git이 아는데 디스크에 없는 파일.

    iCloud가 내용을 evict하면 파일이 사라진 것처럼 보인다.
    이 상태로 커밋하면 삭제가 이력에 박힌다 — e6d3261a가 그랬다.
    """
    return [p for p in g.lines("ls-files", "--deleted") if p.endswith(".md")]


def check_shrunk(g, vault):
    """HEAD 대비 내용이 절반 아래로 줄어든 파일.

    05. VPN.md 는 본문 44줄이 지워지고 목차 14줄이 그 자리에 들어갔다.
    커밋되기 전에 잡아야 한다.
    """
    out = []
    for p in g.lines("diff", "--name-only", "HEAD"):
        if not p.endswith(".md"):
            continue
        head = g.show("HEAD", p)
        if head is None:
            continue
        f = vault / p
        if not f.exists():
            continue
        old = len(head.splitlines())
        new = len(f.read_text(encoding="utf-8", errors="replace").splitlines())
        if old >= SHRINK_MIN_LINES and new < old * SHRINK_RATIO:
            out.append((p, old, new))
    return out


def check_icloud(vault):
    """.icloud 플레이스홀더 = 내용이 evict된 상태."""
    out = []
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            if f.endswith(".icloud"):
                # `.name.md.icloud` → `name.md`
                real = f[1:-7] if f.startswith(".") else f[:-7]
                out.append(str(Path(root).relative_to(vault) / real))
    return out


def check_staged_deletions(g):
    """스테이지에 올라온 .md 삭제. 훅이 쓴다."""
    return [
        p
        for p in g.lines("diff", "--cached", "--name-only", "--diff-filter=D")
        if p.endswith(".md")
    ]


def check_staged_shrunk(g):
    """스테이지에 올라온 내용 급감. 훅이 쓴다."""
    out = []
    for p in g.lines("diff", "--cached", "--name-only", "--diff-filter=M"):
        if not p.endswith(".md"):
            continue
        head = g.show("HEAD", p)
        staged = subprocess.run(
            ["git", "-C", g.root, "show", f":{p}"], capture_output=True
        )
        if head is None or staged.returncode != 0:
            continue
        old = len(head.splitlines())
        new = len(staged.stdout.decode("utf-8", "replace").splitlines())
        if old >= SHRINK_MIN_LINES and new < old * SHRINK_RATIO:
            out.append((p, old, new))
    return out


def cmd_doctor(args):
    vault = Path(args.vault).expanduser()
    if not (vault / ".git").exists():
        print(f"git 저장소가 아니다: {vault}", file=sys.stderr)
        return 2
    g = Git(vault)

    missing = check_missing(g)
    icloud = check_icloud(vault)
    shrunk = check_shrunk(g, vault)

    print(f"vault  {vault}\n")

    if icloud:
        print(f"■ iCloud evict 진행 중 — {len(icloud)}건")
        print("  내용이 클라우드로 내려갔다. 이대로 커밋하면 삭제로 기록된다.")
        for p in icloud[:20]:
            print(f"    {p}")
        if len(icloud) > 20:
            print(f"    … 외 {len(icloud) - 20}")
        print("  → 복구: brctl download <경로>  또는 Finder에서 열어 내려받기\n")

    if missing:
        print(f"■ git에는 있는데 디스크에 없음 — {len(missing)}건")
        for p in missing[:20]:
            print(f"    {p}")
        if len(missing) > 20:
            print(f"    … 외 {len(missing) - 20}")
        print("  → 복구: vault doctor --restore\n")

    if shrunk:
        print(f"■ 내용이 절반 아래로 줄어듦 — {len(shrunk)}건")
        print("  덮어쓰기 사고일 수 있다. 의도한 것이면 넘어가라.")
        for p, old, new in shrunk[:20]:
            print(f"    {old:>5} → {new:<5}줄  {p}")
        if len(shrunk) > 20:
            print(f"    … 외 {len(shrunk) - 20}")
        print("  → 원본: git show HEAD:<경로>\n")

    if args.restore and missing:
        subprocess.run(["git", "-C", str(vault), "checkout", "--", *missing])
        still = check_missing(g)
        print(f"복구 {len(missing) - len(still)}/{len(missing)}건")
        if still:
            print("  실패 (git 인덱스에도 내용이 없다):")
            for p in still:
                print(f"    {p}")
        missing = still

    if not (missing or icloud or shrunk):
        print("\n남은 문제 없음.")
        return 0
    return 1


def split_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    return (m.group(1), text[m.end():]) if m else (None, text)


def validate_frontmatter(fm, body, rel, index, paths):
    """스키마 위반 목록. `vault new` 가 같은 함수를 쓴다."""
    out = []
    if fm is None:
        return [("frontmatter 없음", "")]

    m = re.search(r"^type:\s*(\S+)\s*$", fm, re.M)
    if not m:
        out.append(("type 없음", ""))
    elif m.group(1) not in TYPES:
        out.append(("type가 13값 밖", m.group(1)))

    s = re.search(r"^summary:[ \t]*(.+)$", fm, re.M)
    if s:
        v = s.group(1).strip().strip("\"'")
        if len(v) > SUMMARY_MAX:
            out.append((f"summary {len(v)}자 (상한 {SUMMARY_MAX})", v[:40] + "…"))

    c = re.search(r"^created:\s*(\S+)\s*$", fm, re.M)
    if not c:
        out.append(("created 없음", ""))
    else:
        try:
            # 형태만 보면 2026-13-99 가 통과한다. 실제 날짜인지 확인한다.
            datetime.date.fromisoformat(c.group(1))
        except ValueError:
            out.append(("created 형식 오류", c.group(1)))

    b = re.search(r"^builds_on:\n((?:[ \t]+- .*\n)+)", fm + "\n", re.M)
    if b:
        tgts = [l.strip()[2:].strip().strip("\"'") for l in b.group(1).splitlines()]
        if len(tgts) > BUILDS_ON_MAX:
            out.append((f"builds_on {len(tgts)}개 (상한 {BUILDS_ON_MAX})", ""))
        for t in tgts:
            t = re.sub(r"^\[\[|\]\]$", "", t)
            if not resolve_link(link_target(t), index, paths):
                out.append(("builds_on 미해결", t))

    for tag in find_junk_tags(strip_code(body)):
        out.append(("의도치 않은 태그", tag))
    return out


def cmd_lint(args):
    vault = Path(args.vault).expanduser()
    if not vault.is_dir():
        print(f"디렉토리가 없다: {vault}", file=sys.stderr)
        return 2
    files, index, paths = scan_vault(vault)
    if not files:
        print(f"md 파일이 하나도 없다: {vault}", file=sys.stderr)
        return 2
    ig = load_ignore(vault)
    skills = skill_names(vault)
    show_all = getattr(args, "all", False)

    do_fm = not args.links
    do_ln = not args.frontmatter

    fm_bad, ln_bad, ln_skipped = [], [], 0
    total_links = 0

    for rel in files:
        if show_all is False and rel.startswith(tuple(ig["sources"])):
            skip_src = True
        else:
            skip_src = False
        try:
            text = (vault / rel).read_text(encoding="utf-8")
        except Exception:
            continue
        fm, body = split_frontmatter(text)
        in_ignored_file = rel in ig["files"]

        if do_fm and not skip_src and not (in_ignored_file and not show_all):
            for kind, detail in validate_frontmatter(fm, body, rel, index, paths):
                fm_bad.append((rel, kind, detail))

        if do_ln:
            # 본문만 본다. frontmatter의 builds_on·supersedes는 위에서 이미 검사했다.
            # 둘 다 세면 같은 위반이 두 번 잡힌다.
            for m in LINK.finditer(strip_code(body)):
                t = link_target(m.group(1))
                if not t:
                    continue
                total_links += 1
                if resolve_link(t, index, paths):
                    continue
                if show_all:
                    ln_bad.append((rel, t))
                    continue
                if (skip_src or in_ignored_file or t in ig["targets"]
                        or PLACEHOLDER.match(t) or is_skill_ref(t, skills)):
                    ln_skipped += 1
                    continue
                ln_bad.append((rel, t))

    if do_fm:
        print(f"■ frontmatter — 위반 {len(fm_bad)}건")
        by = {}
        for rel, kind, detail in fm_bad:
            by.setdefault(re.sub(r"\d+", "N", kind), []).append((rel, kind, detail))
        for k in sorted(by, key=lambda x: -len(by[x])):
            print(f"    {len(by[k]):>5}  {k}")
        if args.verbose:
            for rel, kind, detail in fm_bad[: args.limit]:
                print(f"      {kind:<24} {detail[:30]:<32} {rel}")
        print()

    if do_ln:
        print(f"■ 위키링크 {total_links:,}개 — 깨짐 {len(ln_bad)}건 (제외 {ln_skipped}건)")
        cnt = {}
        for rel, t in ln_bad:
            cnt[t] = cnt.get(t, 0) + 1
        for t, n in sorted(cnt.items(), key=lambda x: -x[1])[: args.limit]:
            print(f"    {n:>4}  {t[:70]}")
        if len(cnt) > args.limit:
            print(f"    … 고유 타깃 {len(cnt)}개 중 {args.limit}개만 표시")
        print()

    if args.json:
        Path(args.json).write_text(json.dumps(
            {"frontmatter": [{"file": r, "kind": k, "detail": d} for r, k, d in fm_bad],
             "links": [{"src": r, "target": t} for r, t in ln_bad]},
            ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"→ {args.json}")

    return 1 if (fm_bad or ln_bad) else 0


def fm_blocks(fm):
    """frontmatter를 (키, 그 키가 차지한 줄 전체) 로 쪼갠다.

    `tags:` 처럼 값이 다음 줄들에 있는 블록을 한 덩어리로 유지한다.
    키 줄만 뽑아 쓰면 리스트가 뭉개져 YAML이 깨진다.
    """
    out, key, buf = [], None, []
    for line in (fm or "").split("\n"):
        m = re.match(r"^([\w-]+):", line)
        if m:
            if key is not None:
                out.append((key, "\n".join(buf)))
            key, buf = m.group(1), [line]
        elif key is not None:
            buf.append(line)
    if key is not None:
        out.append((key, "\n".join(buf)))
    return out


def build_frontmatter(type_, summary, builds_on, created, extra=None):
    """스키마 순서대로 frontmatter 텍스트를 만든다.

    extra 는 (키, 줄뭉치) 목록. 초안이 갖고 있던 도메인 필드를 그대로 살린다.
    """
    lines = [f"type: {type_}"]
    if summary:
        lines.append(f"summary: {summary}")
    for _, block in (extra or []):
        lines.append(block.rstrip())
    if builds_on:
        lines.append("builds_on:")
        for b in builds_on:
            b = b.strip()
            if not (b.startswith("[[") and b.endswith("]]")):
                b = f"[[{b}]]"
            lines.append(f'  - "{b}"')
    lines.append(f"created: {created}")
    return "\n".join(lines)


def create_document(vault, rel, fm, body, force=False):
    """검증을 통과한 것만 쓴다. 실패하면 파일을 만들지 않는다.

    `lint` 와 같은 validate_frontmatter() 를 쓴다. 따로 만들면 반드시 어긋난다.
    """
    files, index, paths = scan_vault(vault)
    problems = validate_frontmatter(fm, body, rel, index, paths)

    name = os.path.basename(rel)[:-3]
    bad = BAD_NAME.search(name)
    if bad:
        problems.append(("파일명에 못 쓰는 글자", bad.group(0)))
    if not body.strip():
        problems.append(("본문이 비었다", ""))
    dst = Path(vault) / rel
    if dst.exists() and not force:
        problems.append(("이미 있는 파일", rel))
    if not dst.parent.is_dir():
        problems.append(("없는 디렉토리", str(dst.parent.relative_to(vault))))
    # 같은 이름이 볼트에 이미 있으면 링크가 모호해진다
    if nfc(name) in index and not force:
        others = [p for p in index[nfc(name)] if nfc(p) != nfc(rel)]
        if others:
            problems.append(("같은 파일명이 이미 있다", others[0]))
    return problems


def cmd_new(args):
    vault = Path(args.vault).expanduser()
    if not vault.is_dir():
        print(f"디렉토리가 없다: {vault}", file=sys.stderr)
        return 2

    body = args.body if args.body is not None else sys.stdin.read()
    if not body.strip() and not args.body:
        print("본문이 없다. stdin으로 넣거나 --body 를 준다.", file=sys.stderr)
        return 2

    created = args.created or datetime.date.today().isoformat()
    summary = (args.summary or "").strip()
    if not summary:
        print("--summary 는 필수다. 열지 않고도 고를 수 있어야 한다.", file=sys.stderr)
        return 2

    rel = nfc(str(Path(args.dir) / f"{args.title}.md"))
    fm = build_frontmatter(args.type, summary, args.builds_on, created)

    if args.mkdir:
        (vault / args.dir).mkdir(parents=True, exist_ok=True)

    problems = create_document(vault, rel, fm, body, force=args.force)
    if problems:
        print("만들지 않았다. 스키마를 통과하지 못했다.\n", file=sys.stderr)
        for kind, detail in problems:
            print(f"  {kind:<22} {detail}", file=sys.stderr)
        print("\n태그는 넣지 않는다 — 유저가 직접 단다 (CLAUDE.md 규칙 #3).",
              file=sys.stderr)
        return 1

    warn = routing_warning(rel, args.type)
    text = "---\n" + fm + "\n---\n\n" + body.strip() + "\n"
    (vault / rel).write_text(text, encoding="utf-8")
    print(f"만들었다: {rel}")
    if warn:
        print(f"  경고: {warn}")
    return 0


def cmd_ingest(args):
    """이미 있는 초안을 볼트로 편입한다. frontmatter가 있으면 존중하고 빈 것만 채운다."""
    vault = Path(args.vault).expanduser()
    src = Path(args.draft).expanduser()
    if not src.is_file():
        print(f"초안이 없다: {src}", file=sys.stderr)
        return 2

    raw = src.read_text(encoding="utf-8")
    fm0, body = split_frontmatter(raw)
    blocks = fm_blocks(fm0)
    have = {k: b.split(":", 1)[1].strip() for k, b in blocks}

    type_ = args.type or have.get("type")
    if not type_:
        print("초안에 type이 없다. --type 을 준다.", file=sys.stderr)
        return 2
    summary = (args.summary or have.get("summary", "")).strip()
    if not summary:
        print("--summary 는 필수다.", file=sys.stderr)
        return 2
    created = args.created or have.get("created") or datetime.date.today().isoformat()

    title = args.title or src.stem
    rel = nfc(str(Path(args.dir) / f"{title}.md"))
    # 초안이 갖고 있던 도메인 필드(tags·Author 등)는 살린다
    keep = [(k, b) for k, b in blocks
            if k not in ("type", "summary", "created", "builds_on")]
    fm = build_frontmatter(type_, summary, args.builds_on, created, keep)

    if args.mkdir:
        (vault / args.dir).mkdir(parents=True, exist_ok=True)
    problems = create_document(vault, rel, fm, body, force=args.force)
    if problems:
        print("편입하지 않았다. 스키마를 통과하지 못했다.\n", file=sys.stderr)
        for kind, detail in problems:
            print(f"  {kind:<22} {detail}", file=sys.stderr)
        return 1

    (vault / rel).write_text("---\n" + fm + "\n---\n\n" + body.strip() + "\n",
                             encoding="utf-8")
    print(f"편입했다: {rel}")
    if warn := routing_warning(rel, type_):
        print(f"  경고: {warn}")
    if args.rm:
        src.unlink()
        print(f"  초안 삭제: {src}")
    return 0


# 플러그인이 통째로 복사하는 템플릿. 자기 frontmatter를 못 가진다.
TEMPLATE_PATH = re.compile(r"(^|/)(Templates|_Template)/|(^|/)_template\.md$")

TEMPLATE_HINT = {
    "concept": "무엇인가 / 왜 그런가를 적는다. 읽으면 이해가 남는다.",
    "procedure": "따라 하면 결과가 나오게 적는다. 순서와 확인 지점을 넣는다.",
    "principle": "지켜야 할 규칙과 그 이유. 어길 때 무슨 일이 나는지까지.",
    "decision": "무엇을 골랐고 왜인가. Trade-offs 문서와 쌍으로 만든다.",
    "tradeoff": "선택지를 축으로 비교한다. Decision Node와 쌍으로 만든다.",
    "case": "시간 서사로 적는다. 무엇을 시도했고 무엇이 틀렸는지.",
    "capture": "남의 콘텐츠에서 온 것. 출처를 먼저 밝힌다.",
    "reflection": "자기 성찰. 결론보다 과정을 남긴다.",
    "project-doc": "프로젝트 진행 문서.",
    "reference": "찾아보는 용도. 설명하지 말고 나열한다.",
    "log": "그 시점의 기록. 나중에 고치지 않는다.",
    "hub": "다른 문서를 모으는 인덱스. 링크마다 한 줄 설명을 붙인다.",
    "template": "복사해서 채우는 빈 양식.",
}


def cmd_template(args):
    vault = Path(args.vault).expanduser()
    if args.list:
        files, _, _ = scan_vault(vault)
        rows = []
        for rel in files:
            t = (vault / rel).read_text(encoding="utf-8", errors="replace")
            fm, _ = split_frontmatter(t)
            by_type = bool(fm and re.search(r"^type:\s*template\s*$", fm, re.M))
            # 플러그인이 통째로 복사하는 템플릿은 「태어날 문서」의 frontmatter를
            # 담는다. 그래서 type: template 이 아니다 — 경로로 찾는다.
            by_path = bool(TEMPLATE_PATH.search(rel))
            if not (by_type or by_path):
                continue
            s = re.search(r"^summary:[ \t]*(.+)$", fm or "", re.M)
            mark = "" if by_type else "   (경로로 인식 — 태어날 문서의 frontmatter를 담는다)"
            rows.append((rel, (s.group(1).strip() if s else "") + mark))
        print(f"type: template  {len(rows)}건\n")
        for rel, s in sorted(rows):
            print(f"  {os.path.basename(rel)[:-3]}")
            print(f"      {s[:74]}")
            print(f"      {rel}")
        return 0

    if args.type not in TYPES:
        print(f"type이 13값 밖이다: {args.type}", file=sys.stderr)
        print("  " + " ".join(sorted(TYPES)), file=sys.stderr)
        return 2
    today = datetime.date.today().isoformat()
    print(f"""---
type: {args.type}
summary: {'' if args.bare else '한 줄 요약 — 80자 이내, 제목을 되풀이하지 않는다'}
created: {today}
---

# 제목

{'' if args.bare else TEMPLATE_HINT[args.type]}""")
    return 0


# ── 그래프 (4-b) ──────────────────────────────────────────────────────────
# 정본이 정한 제외 구역. 800 TRPG 는 `type:` 을 게임 아이템 분류로 쓴다
# (완제품 1041 · 원재료 351 · 마물 101). 같은 키, 다른 뜻이라 섞으면 축이 깨진다.
GRAPH_EXCLUDE = ("800 TRPG", "900 Archive", ".claude", ".trash", ".obsidian")
# 노트가 아닌 것. AI 지시문·설정.
GRAPH_EXCLUDE_FILE = ("CLAUDE.md",)

DB_NAME = ".vault-graph.db"

SCHEMA_SQL = """
CREATE TABLE node (
  path    TEXT PRIMARY KEY,   -- 볼트 기준 상대경로
  name    TEXT NOT NULL,      -- 링크에 쓰는 이름 (확장자 없는 파일명)
  zone    TEXT NOT NULL,      -- 최상위 디렉토리
  dir     TEXT NOT NULL,
  type    TEXT,
  summary TEXT,
  created TEXT,
  bytes   INTEGER
);
CREATE INDEX node_name ON node(name);
CREATE INDEX node_type ON node(type);
CREATE INDEX node_zone ON node(zone);

-- kind: builds_on · supersedes (명시) / links_to · part_of (유도)
CREATE TABLE edge (
  src  TEXT NOT NULL,
  dst  TEXT,                  -- 해석 실패면 NULL
  raw  TEXT NOT NULL,         -- 원래 쓰인 타깃 문자열
  kind TEXT NOT NULL
);
CREATE INDEX edge_src ON edge(src, kind);
CREATE INDEX edge_dst ON edge(dst, kind);

CREATE TABLE tag (
  path TEXT NOT NULL,
  tag  TEXT NOT NULL
);
CREATE INDEX tag_tag ON tag(tag);
CREATE INDEX tag_path ON tag(path);

CREATE TABLE meta (k TEXT PRIMARY KEY, v TEXT);
"""

# 사람이 다는 계층 태그만 센다. `#Stack/Python` 처럼 슬래시가 있는 것.
TAG_RE = re.compile(
    r"(?<![\w`\\])#([A-Za-z가-힣][0-9a-zA-Z가-힣_-]*(?:/[0-9a-zA-Z가-힣_-]+)+)")


def fm_list(fm, key):
    m = re.search(rf"^{key}:\n((?:[ \t]+- .*\n)+)", (fm or "") + "\n", re.M)
    if not m:
        return []
    out = []
    for line in m.group(1).splitlines():
        v = line.strip()[2:].strip().strip("\"'")
        out.append(re.sub(r"^\[\[|\]\]$", "", v))
    return out


def cmd_build(args):
    import sqlite3
    vault = Path(args.vault).expanduser()
    if not vault.is_dir():
        print(f"디렉토리가 없다: {vault}", file=sys.stderr)
        return 2
    files, index, paths = scan_vault(vault)
    files = [f for f in files
             if not f.startswith(GRAPH_EXCLUDE) and f not in GRAPH_EXCLUDE_FILE]
    # 제외 구역의 문서도 이름은 안다 — 링크가 그리로 가는지 구분하려면 필요하다
    excluded_names = {nfc(os.path.basename(f)[:-3])
                      for f in scan_vault(vault)[0] if f.startswith(GRAPH_EXCLUDE)}

    db = vault / DB_NAME
    if db.exists():
        db.unlink()
    con = sqlite3.connect(db)
    con.executescript(SCHEMA_SQL)

    # 이름 → 경로. 제외 구역 밖에서만 해석한다.
    live = {}
    for rel in files:
        live.setdefault(nfc(os.path.basename(rel)[:-3]), rel)

    def resolve(raw):
        t = link_target(raw)
        if not t:
            return None
        if "/" in t:
            needle = "/" + t
            for p in files:
                if p == t or p.endswith(needle) or p.endswith(needle + ".md"):
                    return p
            t = nfc(os.path.basename(t)).removesuffix(".md")
        return live.get(t)

    nodes, edges, tags = [], [], []
    for rel in files:
        p = vault / rel
        text = p.read_text(encoding="utf-8", errors="replace")
        fm, body = split_frontmatter(text)
        g = lambda k: (re.search(rf"^{k}:[ \t]*(.+)$", fm or "", re.M) or [None, None])[1]
        d = os.path.dirname(rel)
        nodes.append((rel, nfc(os.path.basename(rel)[:-3]), rel.split("/")[0], d,
                      g("type"), (g("summary") or "").strip(), g("created"),
                      p.stat().st_size))

        for kind in ("builds_on", "supersedes"):
            for raw in fm_list(fm, kind):
                edges.append((rel, resolve(raw), raw, kind))
        for m in LINK.finditer(strip_code(body)):
            raw = m.group(1)
            if link_target(raw):
                edges.append((rel, resolve(raw), raw, "links_to"))
        # 디렉토리 계층 — 부모 디렉토리의 폴더 노트가 있으면 잇는다
        parent = live.get(nfc(os.path.basename(d))) if d else None
        if parent and parent != rel:
            edges.append((rel, parent, os.path.basename(d), "part_of"))
        for m in TAG_RE.finditer(strip_code(body)):
            tags.append((rel, m.group(1)))

    con.executemany("INSERT INTO node VALUES (?,?,?,?,?,?,?,?)", nodes)
    con.executemany("INSERT INTO edge VALUES (?,?,?,?)", edges)
    con.executemany("INSERT INTO tag VALUES (?,?)", tags)
    con.executemany("INSERT INTO meta VALUES (?,?)", [
        ("built", datetime.datetime.now().isoformat(timespec="seconds")),
        ("vault", str(vault)),
        ("excluded", " ".join(GRAPH_EXCLUDE)),
    ])
    con.commit()

    by = dict(con.execute("SELECT kind, count(*) FROM edge GROUP BY kind").fetchall())
    raws = [r[0] for r in con.execute("SELECT raw FROM edge WHERE dst IS NULL")]
    con.close()
    to_excluded = sum(1 for r in raws
                      if nfc(os.path.basename(link_target(r))) in excluded_names)
    print(f"{db.name}  노드 {len(nodes):,} · 엣지 {len(edges):,} · 태그 {len(tags):,}")
    for k, n in sorted(by.items(), key=lambda x: -x[1]):
        print(f"    {n:>6}  {k}")
    print(f"\n  해석 실패 {len(raws):,}")
    print(f"    {to_excluded:>6}  제외 구역(800·900)을 가리킴 — 정상")
    print(f"    {len(raws) - to_excluded:>6}  그 밖 — `vault lint --links` 가 분류한다")
    print(f"  제외: {' · '.join(GRAPH_EXCLUDE)} · {' '.join(GRAPH_EXCLUDE_FILE)}")
    return 0


def _open_db(vault):
    import sqlite3
    db = Path(vault).expanduser() / DB_NAME
    if not db.exists():
        print(f"그래프가 없다. 먼저 `vault build` 를 돌린다.", file=sys.stderr)
        return None
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    return con


def cmd_q(args):
    con = _open_db(args.vault)
    if con is None:
        return 2
    q, a = args.query, args.arg

    def one(name):
        r = con.execute("SELECT * FROM node WHERE name = ? OR path = ?",
                        (nfc(name), nfc(name))).fetchone()
        if not r:
            print(f"그런 문서가 없다: {name}", file=sys.stderr)
        return r

    if q == "path":
        # builds_on 이행 폐쇄 = 「X를 이해하려면 뭘 먼저 봐야 하나」
        r = one(a)
        if not r:
            return 1
        seen, order, stack = set(), [], [(r["path"], 0)]
        while stack:
            cur, d = stack.pop()
            if cur in seen:
                continue
            seen.add(cur)
            order.append((cur, d))
            for e in con.execute(
                "SELECT dst FROM edge WHERE src=? AND kind='builds_on' AND dst IS NOT NULL",
                    (cur,)):
                stack.append((e["dst"], d + 1))
        print(f"{r['name']} 를 이해하려면 — builds_on 이행 폐쇄 {len(order)}개\n")
        for pth, d in order:
            n = con.execute("SELECT * FROM node WHERE path=?", (pth,)).fetchone()
            print(f"{'  ' * d}{'└ ' if d else ''}{n['name']}   [{n['type']}]")
            if n["summary"]:
                print(f"{'  ' * d}   {n['summary'][:70]}")
        if len(order) == 1:
            print("  (전제로 걸린 문서가 없다)")
        return 0

    if q == "orphans":
        rows = con.execute("""
            SELECT n.* FROM node n
            WHERE NOT EXISTS (SELECT 1 FROM edge e
                              WHERE e.dst = n.path AND e.src <> n.path)
            ORDER BY n.zone, n.path""").fetchall()
        if a:
            rows = [r for r in rows if r["zone"].startswith(a) or r["path"].startswith(a)]
        print(f"인바운드 0 — {len(rows)}건\n")
        for r in rows[:args.limit]:
            print(f"  [{r['type'] or '?':<11}] {r['path']}")
        if len(rows) > args.limit:
            print(f"  … {args.limit}개만 표시 (--limit)")
        return 0

    if q == "type":
        rows = con.execute(
            "SELECT * FROM node WHERE type=? ORDER BY path", (a,)).fetchall()
        print(f"type: {a} — {len(rows)}건\n")
        for r in rows[:args.limit]:
            print(f"  {r['name'][:52]:<54} {r['dir'][:48]}")
        return 0

    if q == "tag":
        rows = con.execute("""
            SELECT n.*, count(*) c FROM tag t JOIN node n ON n.path=t.path
            WHERE t.tag = ? GROUP BY n.path ORDER BY c DESC""", (a,)).fetchall()
        print(f"#{a} — {len(rows)}건\n")
        for r in rows[:args.limit]:
            print(f"  [{r['type'] or '?':<11}] {r['name'][:56]}")
        return 0

    if q == "near":
        # 같은 태그 · 링크 이웃. 3·4단계 검색(태그·뜻밖의 발견)이 여기 있다.
        r = one(a)
        if not r:
            return 1
        rows = con.execute("""
            SELECT n.path, n.name, n.type, n.summary,
                   sum(w) score, group_concat(DISTINCT why) why FROM (
              SELECT dst path, 3 w, '링크' why FROM edge
                WHERE src=?1 AND dst IS NOT NULL AND kind='links_to'
              UNION ALL
              SELECT src, 3, '역링크' FROM edge
                WHERE dst=?1 AND kind='links_to'
              UNION ALL
              SELECT t2.path, 2, '태그 #'||t1.tag FROM tag t1 JOIN tag t2
                ON t1.tag=t2.tag WHERE t1.path=?1 AND t2.path<>?1
            ) x JOIN node n ON n.path=x.path
            GROUP BY n.path ORDER BY score DESC, n.name""", (r["path"],)).fetchall()
        print(f"{r['name']} 의 이웃 — {len(rows)}건\n")
        for x in rows[:args.limit]:
            print(f"  {x['score']:>3}  [{x['type'] or '?':<11}] {x['name'][:44]:<46} {x['why'][:34]}")
        return 0

    if q == "stats":
        m = dict(con.execute("SELECT k, v FROM meta").fetchall())
        print(f"빌드 {m.get('built')}   제외 {m.get('excluded')}\n")
        for label, sql in [
            ("구역", "SELECT zone k, count(*) c FROM node GROUP BY zone ORDER BY c DESC"),
            ("type", "SELECT coalesce(type,'(없음)') k, count(*) c FROM node GROUP BY type ORDER BY c DESC"),
            ("엣지", "SELECT kind k, count(*) c FROM edge GROUP BY kind ORDER BY c DESC"),
            ("태그 상위", "SELECT tag k, count(*) c FROM tag GROUP BY tag ORDER BY c DESC LIMIT 10"),
        ]:
            print(f"■ {label}")
            for r in con.execute(sql):
                print(f"    {r['c']:>6}  {r['k']}")
            print()
        return 0

    if q == "sql":
        for r in con.execute(a):
            print("  " + " · ".join(str(v)[:60] for v in r))
        return 0

    print(f"모르는 질의: {q}", file=sys.stderr)
    return 2


def cmd_precommit(args):
    """pre-commit 훅 본체. 사고로 보이는 스테이지를 거부한다."""
    vault = Path(args.vault).expanduser()
    g = Git(vault)

    if os.environ.get("VAULT_ALLOW_DELETE"):
        return 0

    dels = check_staged_deletions(g)
    shrunk = check_staged_shrunk(g)
    if not (dels or shrunk):
        return 0

    print("\n커밋을 멈춘다. 의도하지 않은 유실로 보인다.\n", file=sys.stderr)
    if dels:
        print(f"  삭제 {len(dels)}건", file=sys.stderr)
        for p in dels[:15]:
            print(f"    {p}", file=sys.stderr)
        if len(dels) > 15:
            print(f"    … 외 {len(dels) - 15}", file=sys.stderr)
    if shrunk:
        print(f"\n  내용 급감 {len(shrunk)}건", file=sys.stderr)
        for p, old, new in shrunk[:15]:
            print(f"    {old:>5} → {new:<5}줄  {p}", file=sys.stderr)
        if len(shrunk) > 15:
            print(f"    … 외 {len(shrunk) - 15}", file=sys.stderr)
    print(
        "\n확인했고 의도한 것이라면:\n"
        "    VAULT_ALLOW_DELETE=1 git commit ...\n"
        "\n실수라면 스테이지에서 내린다:\n"
        "    git restore --staged --worktree <경로>\n",
        file=sys.stderr,
    )
    return 1


def cmd_install_hook(args):
    vault = Path(args.vault).expanduser()
    hook = vault / ".git" / "hooks" / "pre-commit"
    if not hook.parent.exists():
        print(f"git 저장소가 아니다: {vault}", file=sys.stderr)
        return 2
    me = Path(__file__).resolve()
    body = f"""#!/bin/sh
# vault-cli 유실 감지. 재설치: python3 {me} install-hook
exec python3 "{me}" pre-commit --vault "{vault}"
"""
    if hook.exists() and "vault-cli" not in hook.read_text():
        backup = hook.with_suffix(".bak")
        backup.write_text(hook.read_text())
        print(f"기존 훅을 {backup.name} 로 옮겼다")
    hook.write_text(body)
    hook.chmod(0o755)
    print(f"설치: {hook}")
    return 0


def main():
    # --vault를 서브커맨드 앞뒤 어디에 써도 먹게 한다.
    # 뒤쪽은 SUPPRESS라, 안 주면 앞쪽 값을 덮어쓰지 않는다.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--vault", default=argparse.SUPPRESS, help="볼트 경로")

    ap = argparse.ArgumentParser(prog="vault", description="Obsidian vault 정합성 도구")
    ap.add_argument("--vault", default=str(DEFAULT_VAULT), help="볼트 경로")
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("doctor", help="유실·손상 검사", parents=[common])
    d.add_argument("--restore", action="store_true", help="사라진 파일을 git에서 되살린다")
    d.set_defaults(fn=cmd_doctor)

    l = sub.add_parser("lint", help="frontmatter·위키링크 정합 검사", parents=[common])
    l.add_argument("--links", action="store_true", help="링크만 검사")
    l.add_argument("--frontmatter", action="store_true", help="frontmatter만 검사")
    l.add_argument("--all", action="store_true", help="제외 규칙 없이 전부 센다")
    l.add_argument("--verbose", "-v", action="store_true", help="위반을 하나씩 나열")
    l.add_argument("--limit", type=int, default=30, help="나열 상한 (기본 30)")
    l.add_argument("--json", metavar="경로", help="결과를 JSON으로 저장")
    l.set_defaults(fn=cmd_lint)

    n = sub.add_parser("new", help="스키마를 통과한 문서만 만든다", parents=[common])
    n.add_argument("--type", required=True, choices=sorted(TYPES), metavar="TYPE")
    n.add_argument("--title", required=True, help="파일명이 된다 (.md 없이)")
    n.add_argument("--dir", required=True, help="볼트 기준 상대 디렉토리")
    n.add_argument("--summary", required=True, help=f"{SUMMARY_MAX}자 이내")
    n.add_argument("--builds-on", action="append", default=[],
                   dest="builds_on", metavar="[[문서]]",
                   help=f"전제 개념. 최대 {BUILDS_ON_MAX}회")
    n.add_argument("--body", help="본문. 없으면 stdin에서 읽는다")
    n.add_argument("--created", help="기본값은 오늘")
    n.add_argument("--mkdir", action="store_true", help="없는 디렉토리를 만든다")
    n.add_argument("--force", action="store_true", help="같은 이름·기존 파일 검사를 건너뛴다")
    n.set_defaults(fn=cmd_new)

    g = sub.add_parser("ingest", help="기존 초안을 볼트로 편입한다", parents=[common])
    g.add_argument("draft", help="초안 파일 경로")
    g.add_argument("--dir", required=True)
    g.add_argument("--type", help="초안 frontmatter에 있으면 생략 가능")
    g.add_argument("--title", help="기본값은 초안 파일명")
    g.add_argument("--summary")
    g.add_argument("--builds-on", action="append", default=[], dest="builds_on")
    g.add_argument("--created")
    g.add_argument("--mkdir", action="store_true")
    g.add_argument("--force", action="store_true")
    g.add_argument("--rm", action="store_true", help="편입 후 초안을 지운다")
    g.set_defaults(fn=cmd_ingest)

    t = sub.add_parser("template", help="스키마 뼈대 출력 / --list", parents=[common])
    t.add_argument("--type", default="concept", metavar="TYPE")
    t.add_argument("--list", action="store_true", help="type:template 문서를 나열한다")
    t.add_argument("--bare", action="store_true", help="설명 없이 뼈대만")
    t.set_defaults(fn=cmd_template)

    b = sub.add_parser("build", help="그래프를 SQLite로 빌드한다", parents=[common])
    b.set_defaults(fn=cmd_build)

    qp = sub.add_parser("q", help="그래프 질의", parents=[common])
    qp.add_argument("query", choices=["path", "orphans", "type", "tag", "near", "stats", "sql"])
    qp.add_argument("arg", nargs="?", help="질의 인자")
    qp.add_argument("--limit", type=int, default=30)
    qp.set_defaults(fn=cmd_q)

    p = sub.add_parser("pre-commit", help="훅 본체 (직접 부를 일 없음)", parents=[common])
    p.set_defaults(fn=cmd_precommit)

    i = sub.add_parser("install-hook", help="pre-commit 훅 설치", parents=[common])
    i.set_defaults(fn=cmd_install_hook)

    args = ap.parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()
