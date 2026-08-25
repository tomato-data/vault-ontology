"""The tag vocabulary — the whitelist an agent tags from, never inventing.

`vault tags` is read-only on purpose. Adding a tag to the vocabulary is a
separate, deliberate act (by hand, or a future command), so an agent given
this list cannot grow the vocabulary — which is exactly the failure mode
that made auto-tagging unpleasant before.
"""

from collections import Counter

from vault.frontmatter import fm_list, split_frontmatter
from vault.graph import in_graph
from vault.scan import scan_vault


def tag_vocabulary(root):
    """Every tag in the graph zones with its note count, commonest first."""
    counts = Counter()
    notes, _, _ = scan_vault(root)
    for relative in notes:
        if not in_graph(relative):
            continue
        fm, _ = split_frontmatter((root / relative).read_text(encoding="utf-8"))
        counts.update(fm_list(fm, "tags"))
    return counts.most_common()
