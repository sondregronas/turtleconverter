from turtleconverter import mdfile_to_html, mdfile_to_sections


def test_mdfile_to_html_preprocesses_markdown(tmp_path):
    input_file = tmp_path / "input.md"
    input_file.write_text("# Original\n", encoding="utf-8")

    html = mdfile_to_html(
        input_file,
        preprocess=lambda markdown: f"{markdown}\nAdded by preprocess",
    )

    assert "Added by preprocess" in html


def test_mdfile_to_sections_preprocesses_markdown(tmp_path):
    input_file = tmp_path / "input.md"
    input_file.write_text("# Original\n", encoding="utf-8")

    sections = mdfile_to_sections(
        input_file,
        preprocess=lambda markdown: f"{markdown}\nAdded by preprocess",
    )

    assert "Added by preprocess" in sections["body"]
