from turtleconverter import mdfile_to_sections


def _convert(tmp_path, markdown, **kwargs):
    input_file = tmp_path / "input.md"
    input_file.write_text(markdown, encoding="utf-8")
    return mdfile_to_sections(input_file, **kwargs)["body"]


def test_custom_emoji_url(tmp_path):
    body = _convert(tmp_path, "Easy :diff1:\n", emojis={"diff1": "/static/diff1.png"})

    assert '<img alt=":diff1:" class="twemoji" src="/static/diff1.png" title=":diff1:"' in body


def test_custom_emoji_attributes(tmp_path):
    emojis = {"diff1": {"src": "/static/diff1.png", "alt": "Easy", "class": "emote"}}
    body = _convert(tmp_path, "Easy :diff1:\n", emojis=emojis)

    assert '<img alt="Easy" class="emote" src="/static/diff1.png" title=":diff1:"' in body


def test_custom_emoji_is_not_replaced_in_code(tmp_path):
    body = _convert(tmp_path, "`:diff1:`\n\n```\n:diff1:\n```\n", emojis={"diff1": "/static/diff1.png"})

    assert "/static/diff1.png" not in body
    assert ":diff1:" in body


def test_twemoji_still_works_with_custom_emojis(tmp_path):
    body = _convert(tmp_path, ":smile: :diff1:\n", emojis={"diff1": "/static/diff1.png"})

    assert "1f604.svg" in body
    assert "/static/diff1.png" in body


def test_custom_emojis_are_per_conversion(tmp_path):
    _convert(tmp_path, ":diff1:\n", emojis={"diff1": "/static/diff1.png"})
    body = _convert(tmp_path, ":diff1:\n")

    assert "/static/diff1.png" not in body
    assert ":diff1:" in body
