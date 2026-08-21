"""Which findings the vault has decided not to hear about.

The list lives in `.vault-lint.json` at the vault root, never in here, and
that file is committed: what was excluded and why has to be auditable.
"""

import json

from vault.frontmatter import fm_list, split_frontmatter
from vault.links import iter_links, link_target
from vault.scan import resolve_link, scan_vault
from vault.schema import find_body_tags, validate

CONFIG_NAME = ".vault-lint.json"

# Empty on purpose. Without a config the linter checks everything, and a
# vault that wants an exemption has to write it down where it can be read.
DEFAULTS = {
    "skip_unresolved_from": [],  # a zone whose broken links point at the past
    "skip_unresolved_to": [],  # a template placeholder, not a document
    "skip_frontmatter_in": [],  # a zone carrying a schema of its own
    "skip_files": [],  # not a note at all
}


def load_rules(root):
    """Read `.vault-lint.json`, filled out with the defaults.

    Merged key by key. A config naming one key must not drop the other
    three — a config file is normally written in part.
    """
    config = root / CONFIG_NAME
    user = json.loads(config.read_text(encoding="utf-8")) if config.exists() else {}
    return {key: user.get(key, list(default)) for key, default in DEFAULTS.items()}


def _under(path, zones):
    """True when `path` lies in one of `zones`, counted by directory."""
    return any(path == zone or path.startswith(zone + "/") for zone in zones)


def skips_frontmatter(rules, path):
    """True when this document's frontmatter is not to be checked."""
    return path in rules["skip_files"] or _under(path, rules["skip_frontmatter_in"])


def skips_unresolved(rules, source, target):
    """True when this unresolved link is not to be reported."""
    return (
        source in rules["skip_files"]
        or _under(source, rules["skip_unresolved_from"])
        or target in rules["skip_unresolved_to"]
    )


def lint_vault(root):
    """Return every finding in the vault as (path, code, detail).

    Findings, not printed lines: the caller picks the format and the exit
    code. Same decision as `validate` returning a list instead of raising,
    one layer up.
    """
    rules = load_rules(root)
    notes, index, targets = scan_vault(root)
    findings = []

    for relative in notes:
        fm, body = split_frontmatter((root / relative).read_text(encoding="utf-8"))

        # Schema checks. A zone with a schema of its own answers to nobody
        # here — including for the tags in its body, which are schema too.
        if not skips_frontmatter(rules, relative):
            findings += [(relative, code, detail) for code, detail in validate(fm)]
            findings += [(relative, "body tag", tag) for tag in find_body_tags(body)]
            for item in fm_list(fm, "builds_on"):
                target = link_target(item)
                if resolve_link(target, index, targets, source=relative) is None:
                    findings.append((relative, "builds_on unresolved", target))

        # Body links are gated separately, so a zone whose broken links
        # point at the past still gets its frontmatter checked.
        for target in iter_links(body):
            if resolve_link(
                target, index, targets, source=relative
            ) is None and not skips_unresolved(rules, relative, target):
                findings.append((relative, "link unresolved", target))

    return findings
