"""Check the graph against the vault's shapes.

`vault-ontology.ttl` says what follows from the data; `vault-shapes.ttl`
says what the vault requires of it. Phase 9 spent a phase proving those are
different things — a `domain` mistyped 764 folders because it was read as a
rule when it was a derivation — so the two files never merge.

Nothing here infers. pyshacl is given the data as it stands, so a shape
reports on what is written and not on what could be worked out.
"""

from collections import Counter
from pathlib import Path

import pyshacl
from rdflib import Graph
from rdflib.namespace import SH

from vault.rdf import doc_path, section_path

SHAPES_NAME = "vault-shapes.ttl"

# Where a finding is reported, worst first. A report that is not ordered is
# a report that gets read from the top and abandoned.
SEVERITY = {SH.Violation: "violation", SH.Warning: "warning", SH.Info: "info"}
ORDER = {"violation": 0, "warning": 1, "info": 2}


def shapes_graph(root=None):
    """Load the shapes. `root` defaults to this repository."""
    path = Path(root) if root else Path(__file__).parent.parent
    return Graph().parse(path / SHAPES_NAME, format="turtle")


def _where(node):
    """Turn a focus node IRI into a place a person can open.

    A section IRI carries its heading, so a finding about one item does not
    say "somewhere in this file of 24 insights".
    """
    text = str(node)
    if "#" in text:
        path, heading = section_path(node)
        return path, heading
    return doc_path(node), ""


def findings(data, shapes):
    """Return every finding as a dict, worst first.

    The dict, and not pyshacl's report graph, is what the rest of the code
    sees. A report graph would put the caller back in the business of
    walking blank nodes to answer "what broke, and where do I go".
    """
    conforms, report, _ = pyshacl.validate(
        data, shacl_graph=shapes, advanced=True, inference="none"
    )
    found = []
    for result in report.subjects(SH.resultSeverity, None):
        node = report.value(result, SH.focusNode)
        if node is None:
            continue
        path, heading = _where(node)
        severity = SEVERITY.get(report.value(result, SH.resultSeverity), "info")
        # A node-level constraint reports the focus node as its own value.
        # Printing it repeats the path as an IRI and says nothing.
        value = report.value(result, SH.value)
        found.append(
            {
                "severity": severity,
                "shape": str(report.value(result, SH.sourceShape)),
                "message": str(report.value(result, SH.resultMessage) or ""),
                "path": path,
                "heading": heading,
                "value": "" if value is None or value == node else str(value),
            }
        )
    # Worst first, then by file, so a person reads the report top down and
    # the second run puts the same lines in the same order.
    found.sort(key=lambda f: (ORDER[f["severity"]], f["path"], f["heading"]))
    return conforms, found


def summarise(found):
    """Count findings by severity and by message."""
    return Counter(f["severity"] for f in found), Counter(f["message"] for f in found)


def format_finding(finding):
    """One line, `path:heading` first so an editor can jump to it."""
    where = finding["path"]
    if finding["heading"]:
        where += f"#{finding['heading']}"
    line = f"{where}: [{finding['severity']}] {finding['message']}"
    if finding["value"]:
        line += f" — {finding['value']}"
    return line
