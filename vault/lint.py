"""Which findings the vault has decided not to hear about.

The list lives in `.vault-lint.json` at the vault root, never in here, and
that file is committed: what was excluded and why has to be auditable.
"""

import json

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
