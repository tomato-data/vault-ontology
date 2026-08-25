from vault.tags import tag_vocabulary


def note(*tags):
    block = "".join(f"  - {t}\n" for t in tags)
    head = f"tags:\n{block}" if tags else ""
    return f"---\ntype: concept\n{head}summary: ok\ncreated: 2026-08-10\n---\n본문\n"


def make(tmp_path, files):
    for relative, text in files.items():
        p = tmp_path / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return tmp_path


def test_vocabulary_counts_notes_and_sorts_by_frequency(tmp_path):
    root = make(tmp_path, {
        "200 Dev/a.md": note("Stack/Python", "Source/Claude"),
        "200 Dev/b.md": note("Stack/Python"),
        "200 Dev/c.md": note(),
    })
    assert tag_vocabulary(root) == [("Stack/Python", 2), ("Source/Claude", 1)]


def test_excluded_zones_do_not_enter_the_vocabulary(tmp_path):
    root = make(tmp_path, {
        "200 Dev/a.md": note("Stack/Python"),
        "900 Archive/old.md": note("Stack/Legacy"),
    })
    vocab = dict(tag_vocabulary(root))
    assert "Stack/Legacy" not in vocab
