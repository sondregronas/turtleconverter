"""
Usage:
    mdfile_to_section = mdfile_to_sections(Path('test.md'), static_folder=Path('static'), assets_folder=Path('turtleconvert'))
        This will return a dictionary of HTML content divided into sections (heading, head, body and meta), and the
        assets folder will be placed in the static folder. (static/turtleconvert/javascripts | stylesheets in this case)

    mdfile_to_html = mdfile_to_html(Path('test.md'), static_folder=Path('static'), assets_folder=Path('turtleconvert'), include_metadata: bool = False)
        Same as above, but will return the full HTML content as a string. Returns a tuple with the metadata if include_metadata is True.
"""

import re
from pathlib import Path

try:
    from .mkdocs_build_override import MKDOCS_CONFIG, _build
except ImportError:
    from mkdocs_build_override import MKDOCS_CONFIG, _build


def _str_to_path_mass_convert(list_of_values: list) -> list:
    """Converts a list of strings to a list of Path objects."""
    return [Path(value) if isinstance(value, str) else value for value in list_of_values]


def mdfile_to_html(md_file_path: Path, static_folder: Path = Path('static'),
                   assets_folder: Path = Path('turtleconvert'), include_metadata: bool = False) -> str or tuple:
    """Converts a markdown file to a html file."""
    md_file_path, static_folder, assets_folder = _str_to_path_mass_convert([md_file_path, static_folder, assets_folder])

    page, meta = _build(md_file_path, static_folder / assets_folder, MKDOCS_CONFIG)

    # Replace the relative paths with the absolute paths
    page = page.replace('../assets/', f'/{static_folder}/{assets_folder}/')
    page = page.replace('../assets/', f'/{static_folder}/{assets_folder}/')

    if include_metadata:
        return page, meta
    return page


def mdfile_to_sections(md_file_path: Path, static_folder: Path = Path('static'),
                       assets_folder: Path = Path('turtleconvert'), isolate_heading: bool = True) -> dict:
    """Returns a dictionary of HTML content divided into sections."""
    md_file_path, static_folder, assets_folder = _str_to_path_mass_convert([md_file_path, static_folder, assets_folder])

    page, meta = mdfile_to_html(md_file_path, static_folder, assets_folder, include_metadata=True)

    regex = re.compile(r"<head.*?>(.*?)</head>.*?<body.*?>(.*?)</body>", re.DOTALL)
    results = regex.findall(page)

    h1_tag = meta.get('title', re.search(r'<h1.*?\>(.+?)\<\/h1>', results[0][1]).group(1))

    head = results[0][0]
    body = results[0][1]

    if isolate_heading:
        body = re.sub(r'<h1.*?\>(.+?)\<\/h1>', '', body, count=1)

    return {
        'heading': h1_tag,
        'head': head,
        'body': body,
        'meta': meta
    }


if __name__ == '__main__':
    # Testing data, feel free to ignore this
    print(mdfile_to_sections('test.md'))
    data = mdfile_to_html(Path('test.md'))
    with open('static/test.html', 'w', encoding='utf-8') as f:
        f.write(data)
