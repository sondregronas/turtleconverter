from turtleconverter import mdfile_to_sections


def test_remove_matching_heading(tmp_path):
    input_markdown = """\
---
title: Title
---

# Title

Body
"""
    input_file = tmp_path / "input.md"
    input_file.write_text(input_markdown, encoding="utf-8")

    sections = mdfile_to_sections(
        input_file,
        remove_heading=False,
        remove_heading_if_title_matches=True,
    )

    assert sections["meta"]["title"] == "Title"
    assert '<h1 id="title">Title</h1>' not in sections["body"]
    assert "<p>Body</p>" in sections["body"]


def test_title_with_h2(tmp_path):
    input_markdown = """\
---
title: Title
---

## Heading 2
"""
    input_file = tmp_path / "input.md"
    input_file.write_text(input_markdown, encoding="utf-8")

    sections = mdfile_to_sections(input_file)

    assert sections["meta"]["title"] == "Title"
    assert sections["heading"] == "Title"
    assert "<h1" not in sections["body"]
    assert '<h2 id="heading-2">Heading 2</h2>' in sections["body"]


def test_keep_matching_heading(tmp_path):
    input_markdown = """\
---
title: Title
---

# Title
"""
    input_file = tmp_path / "input.md"
    input_file.write_text(input_markdown, encoding="utf-8")

    sections = mdfile_to_sections(
        input_file,
        remove_heading=False,
        remove_heading_if_title_matches=False,
    )

    assert sections["meta"]["title"] == "Title"
    assert '<h1 id="title">Title</h1>' in sections["body"]


def test_keep_different_heading(tmp_path):
    input_markdown = """\
---
title: Title
---

# Title2
"""
    input_file = tmp_path / "input.md"
    input_file.write_text(input_markdown, encoding="utf-8")

    sections = mdfile_to_sections(input_file, remove_heading=False)

    assert sections["meta"]["title"] == "Title"
    assert '<h1 id="title2">Title2</h1>' in sections["body"]


def test_remove_matching_generated_title(tmp_path):
    input_markdown = """\
---
title: Title
---

## Heading 2
"""
    input_file = tmp_path / "input.md"
    input_file.write_text(input_markdown, encoding="utf-8")

    sections = mdfile_to_sections(
        input_file,
        remove_heading=False,
        remove_heading_if_title_matches=True,
    )

    assert "<h1>Title</h1>" not in sections["body"]
    assert '<h2 id="heading-2">Heading 2</h2>' in sections["body"]


def test_remove_heading_explicitly(tmp_path):
    input_markdown = """\
---
title: Title
---

# Heading
"""
    input_file = tmp_path / "input.md"
    input_file.write_text(input_markdown, encoding="utf-8")

    sections = mdfile_to_sections(input_file, remove_heading=False)
    removed_sections = mdfile_to_sections(input_file, remove_heading=True)

    assert '<h1 id="heading">Heading</h1>' in sections["body"]
    assert '<h1 id="heading">Heading</h1>' not in removed_sections["body"]


def test_remove_escaped_title(tmp_path):
    input_markdown = """\
---
title: Inline & Ekstern CSS
---

## Inline CSS
"""
    input_file = tmp_path / "input.md"
    input_file.write_text(input_markdown, encoding="utf-8")

    sections = mdfile_to_sections(
        input_file, remove_heading=False, remove_heading_if_title_matches=True
    )

    assert "<h1" not in sections["body"]
    assert "<h1>Inline &amp; Ekstern CSS</h1>" not in sections["body"]
    assert '<h2 id="inline-css">Inline CSS</h2>' in sections["body"]
