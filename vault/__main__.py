"""Command line entry point: `python -m vault lint`."""

import argparse
import sqlite3
import sys
from collections import Counter
from pathlib import Path

from vault.graph import (
    DB_NAME,
    build,
    by_tag,
    by_type,
    find,
    learning_path,
    near,
    orphans,
    stats,
)
from vault.lint import lint_vault
from vault.rdf import TTL_NAME, build_graph

DEFAULT_VAULT = Path.home() / (
    "Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault"
)


def _parser():
    # One shared `--vault`, added to each leaf so it may follow the command
    # the way a person types it: `vault q stats --vault …`.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--vault", type=Path, default=DEFAULT_VAULT)

    parser = argparse.ArgumentParser(prog="vault")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("lint", parents=[common], help="check against the schema")
    commands.add_parser("build", parents=[common], help="write the graph")
    commands.add_parser("rdf", parents=[common], help="write the RDF graph")

    queries = commands.add_parser("q", help="ask the graph").add_subparsers(
        dest="query", required=True
    )
    queries.add_parser("stats", parents=[common])
    for name, argument in (
        ("path", "note"),
        ("near", "note"),
        ("type", "type"),
        ("tag", "tag"),
    ):
        queries.add_parser(name, parents=[common]).add_argument(argument)
    queries.add_parser("orphans", parents=[common]).add_argument("zone", nargs="?")
    return parser


def main(argv=None):
    """Run a command and return its exit code.

    0 clean · 1 violations found · 2 could not run. A tool that only
    prints cannot go in CI or a pre-commit hook; the exit code is the
    part a machine reads.
    """
    args = _parser().parse_args(argv)
    if not args.vault.is_dir():
        print(f"vault: no such directory: {args.vault}", file=sys.stderr)
        return 2

    if args.command == "lint":
        findings = lint_vault(args.vault)
        for path, code, detail in findings:
            print(f"{path}: {code}" + (f" — {detail}" if detail else ""))
        print(f"{len(findings):,} violations", file=sys.stderr)
        return 1 if findings else 0

    if args.command == "build":
        counts = stats(build(args.vault, args.vault / DB_NAME))
        print(
            f"{DB_NAME}  노드 {counts['node']:,} · 엣지 {counts['edge']:,}"
            f" · 태그 {counts['tag']:,}"
        )
        for kind, n in sorted(counts["kinds"].items(), key=lambda kv: -kv[1]):
            print(f"  {n:7,}  {kind}")
        print(f"  {counts['unresolved']:7,}  해석 실패")
        return 0

    if args.command == "rdf":
        graph = build_graph(args.vault)
        graph.serialize(destination=args.vault / TTL_NAME, format="turtle")
        print(f"{TTL_NAME} 트리플 {len(graph):,}")
        for prefix, count in _predicate_counts(graph):
            print(f"  {count:7,}  {prefix}")
        return 0

    database = args.vault / DB_NAME
    if not database.exists():
        print(
            f"vault: {DB_NAME} 가 없다. `vault build` 를 먼저 돌린다.", file=sys.stderr
        )
        return 2
    return _query(sqlite3.connect(database), args)


def _query(connection, args):
    if args.query == "stats":
        counts = stats(connection)
        for key in ("node", "edge", "tag", "unresolved"):
            print(f"  {counts[key]:7,}  {key}")
        for kind, n in sorted(counts["kinds"].items(), key=lambda kv: -kv[1]):
            print(f"  {n:7,}  {kind}")
        return 0

    if args.query == "type":
        for path in by_type(connection, args.type):
            print(path)
        return 0

    if args.query == "tag":
        for path in by_tag(connection, args.tag):
            print(path)
        return 0

    if args.query == "orphans":
        for path in orphans(connection, args.zone):
            print(path)
        return 0

    start = find(connection, args.note)
    if start is None:
        print(f"vault: 그런 문서가 없다: {args.note}", file=sys.stderr)
        return 2

    if args.query == "path":
        print(f"{start} 를 이해하려면\n")
        for target, depth in learning_path(connection, start):
            print(f"  {depth}  {target}")
        return 0

    neighbours = near(connection, start)
    print(f"{start} 의 이웃\n")
    for key in ("links_to", "linked_by"):
        print(f"  {key}")
        for path in neighbours[key]:
            print(f"      {path}")
    print("  shares_tag  (공유 태그 수 · 많은 순)")
    for path, count in neighbours["shares_tag"][:20]:
        print(f"      {count}  {path}")
    return 0


def _predicate_counts(graph):
    """Predicates by how often they are stated, most first."""
    counts = Counter(str(p).rsplit("/", 1)[-1].rsplit("#", 1)[-1] for _, p, _ in graph)
    return counts.most_common()


if __name__ == "__main__":
    sys.exit(main())
