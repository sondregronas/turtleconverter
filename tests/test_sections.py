from turtleconverter import mdfile_to_sections


def test_mdfile_to_sections_removes_matching_title_heading_when_enabled(tmp_path):
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


def test_mdfile_to_sections_does_not_require_heading_for_frontmatter_title(tmp_path):
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


def test_mdfile_to_sections_can_preserve_matching_title_heading(tmp_path):
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


def test_mdfile_to_sections_preserves_different_title_heading(tmp_path):
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
    assert "Title2" in sections["body"]


def test_mdfile_to_sections_does_not_remove_generated_title_before_h2(
    tmp_path,
):
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

    assert "<h1>Title</h1>" in sections["body"]
    assert '<h2 id="heading-2">Heading 2</h2>' in sections["body"]


def test_mdfile_to_sections_remove_heading_remains_explicit(tmp_path):
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
