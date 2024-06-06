"""
Usage:
    mdfile_to_section = mdfile_to_sections(Path('test.md'), static_folder=Path('static'), assets_folder=Path('turtleconvert'))
        This will return a dictionary of HTML content divided into sections (head and body), and the assets folder will be placed in the static folder.
        (static/turtleconvert/javascripts and static/turtleconvert/stylesheets in this case)

    mdfile_to_html = mdfile_to_html(Path('test.md'), static_folder=Path('static'), assets_folder=Path('turtleconvert'))
        Same as above, but will return the full HTML content as a string.
"""

import re
from pathlib import Path

from .mkdocs_build_override import MKDOCS_CONFIG, _build


def mdfile_to_html(md_file_path: Path, static_folder: Path = Path('static'),
                   assets_folder: Path = 'turtleconvert') -> str:
    """Converts a markdown file to a html file."""
    page = _build(md_file_path, static_folder / assets_folder, MKDOCS_CONFIG)

    # Replace the relative paths with the absolute paths
    page = page.replace('../assets/', f'../{static_folder}/{assets_folder}/')
    page = page.replace('../assets/', f'../{static_folder}/{assets_folder}/')

    return page


def mdfile_to_sections(md_file_path: Path, static_folder: Path = Path('static'),
                       assets_folder: Path = 'turtleconvert', isolate_heading: bool = True) -> dict:
    """Returns a dictionary of HTML content divided into sections."""
    page = mdfile_to_html(md_file_path, static_folder, assets_folder)

    regex = re.compile(r"<head.*?>(.*?)</head>.*?<body.*?>(.*?)</body>", re.DOTALL)
    results = regex.findall(page)

    h1_tag = re.search(r'<h1.+?\>(.+?)\<\/h1>', results[0][1]).group(1)

    head = results[0][0]
    body = results[0][1]

    if isolate_heading:
        body = re.sub(r'<h1.+?\>(.+?)\<\/h1>', '', body, count=1)

    return {
        'heading': h1_tag,
        'head': head,
        'body': body
    }
