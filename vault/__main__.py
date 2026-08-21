"""Command line entry point: `python -m vault lint`."""

import argparse
import sys
from pathlib import Path

from vault.lint import lint_vault

DEFAULT_VAULT = Path.home() / (
    "Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault"
)


def main(argv=None):
    """Run a command and return its exit code.

    0 clean · 1 violations found · 2 could not run. A tool that only
    prints cannot be put in CI or a pre-commit hook; the exit code is the
    part a machine reads.
    """
    parser = argparse.ArgumentParser(prog="vault")
    commands = parser.add_subparsers(dest="command", required=True)
    lint = commands.add_parser("lint", help="check every note against the schema")
    lint.add_argument("--vault", type=Path, default=DEFAULT_VAULT)

    args = parser.parse_args(argv)
    if not args.vault.is_dir():
        print(f"vault: no such directory: {args.vault}", file=sys.stderr)
        return 2

    findings = lint_vault(args.vault)
    for path, code, detail in findings:
        print(f"{path}: {code}" + (f" - {detail}" if detail else ""))
    print(f"{len(findings):,} violations", file=sys.stderr)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
