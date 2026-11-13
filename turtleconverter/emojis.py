"""
Custom emoji for pymdownx.emoji: extra `:name:` shortcodes rendered as images, on top of Material's twemoji set.

The shortcodes are read from the extension's `custom_emojis` option, which `_build()` sets for every page from the
`emojis` argument. Each one maps to an image url, or to a dict of <img> attributes (at least "src").
"""

from collections import ChainMap
from xml.etree.ElementTree import Element

from material.extensions import emoji as material_emoji


def twemoji(options: dict, md) -> dict:
    """Material's twemoji index, extended with the custom emojis."""
    index = material_emoji.twemoji(options, md)
    custom = {f":{name}:": {"name": f":{name}:", "category": "custom"} for name in options.get("custom_emojis", {})}
    # Material caches its index, so it is layered rather than updated
    return {**index, "emoji": ChainMap(custom, index["emoji"])}


def to_svg(index, shortname, alias, uc, alt, title, category, options, md):
    """Render custom emojis as <img> elements, and every other emoji the way Material does."""
    image = options.get("custom_emojis", {}).get(shortname[1:-1])
    if image is None:
        return material_emoji.to_svg(index, shortname, alias, uc, alt, title, category, options, md)

    attributes = {"class": options.get("classes", index), "alt": alt}
    if title:
        attributes["title"] = title
    attributes.update({"src": image} if isinstance(image, str) else image)
    return Element("img", attributes)
