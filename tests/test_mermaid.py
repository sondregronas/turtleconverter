from pathlib import Path

from turtleconverter import generate_static_files, mdfile_to_html


def test_sequence_mermaid_theme_covers_solid_and_dashed_arrowheads(tmp_path):
    input_file = tmp_path / "sequence.md"
    input_file.write_text(
        """\
---
title: Sequence
---

```mermaid
sequenceDiagram
    Alice->>Bob: Solid message
    Bob-->>Alice: Dashed message
```
""",
        encoding="utf-8",
    )

    html = mdfile_to_html(input_file)
    static_folder = tmp_path / "static"
    generate_static_files(static_folder)
    mermaid_bundle = next(
        (static_folder / "turtleconvert" / "javascripts").glob("bundle.*.min.js")
    )
    mermaid_theme = mermaid_bundle.read_text(encoding="utf-8")

    assert "Alice-&gt;&gt;Bob: Solid message" in html
    assert "Bob--&gt;&gt;Alice: Dashed message" in html
    assert r'[id$=\"-arrowhead\"] path' in mermaid_theme
    assert r'[id$=\"-filled-head\"] path' in mermaid_theme
    assert r'[id$=\"-crosshead\"] path' in mermaid_theme
    assert (
        "fill:var(--md-mermaid-sequence-message-line-color)!important" in mermaid_theme
    )
    assert (
        "stroke:var(--md-mermaid-sequence-message-line-color)!important" in mermaid_theme
    )
    assert "marker{fill:var(--md-mermaid-edge-color)!important}" in mermaid_theme
    assert (
        ".actor,.actor-line,.messageLine0,.messageLine1,.loopLine,line,rect{"
        "stroke-width:var(--md-mermaid-stroke-width,1px)!important}"
    ) in mermaid_theme
    assert '}".actor,.actor-line' not in mermaid_theme
