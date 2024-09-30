"""Slow and steady conversion of singular markdown files to HTML files. See the README for more information."""

import re
import tempfile
from pathlib import Path

try:
    from .mkdocs_build_override import MKDOCS_CONFIG, _build, ConversionError  # noqa
except ImportError:
    from mkdocs_build_override import MKDOCS_CONFIG, _build, ConversionError  # noqa


def _str_to_path_mass_convert(list_of_values: list) -> list:
    """Converts a list of strings to a list of Path objects."""
    return [Path(value) if isinstance(value, str) else value for value in list_of_values]


def generate_static_files(static_folder: Path = Path('static'), assets_folder: Path = Path('turtleconvert')) -> None:
    """Generates the static files for the HTML file."""
    static_folder, assets_folder = _str_to_path_mass_convert([static_folder, assets_folder])
    _build(None, static_folder / assets_folder, MKDOCS_CONFIG, only_static_files=True)


# If we only have a single newline after ``` or |, add a second \n
newline_blockers = [r'```', r'\|']
except_on = ['\n', r'\|']
newline_regex = re.compile(rf'({"|".join(newline_blockers)})\n(?!{"|".join(except_on)})')
print(newline_regex)


def ensure_nl2br(md_file_path: Path) -> Path:
    """Ensures that all newlines in a markdown file are converted to <br> tags."""
    # Create a temporary file in memory to store the new content
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8') as f:
        f.write(newline_regex.sub(r'\1\n\n', content))
    return Path(f.name)


def mdfile_to_html(md_file_path: Path, static_folder: Path = Path('static'),
                   assets_folder: Path = Path('turtleconvert'), include_metadata: bool = False,
                   abspath: bool = True, template: Path = 'turtleconvert.html',
                   generate_static_files: bool = False) -> str or tuple:
    """Converts a markdown file to a html file."""
    md_file_path, static_folder, assets_folder = _str_to_path_mass_convert([md_file_path, static_folder, assets_folder])
    # Create a temporary file to store the new content so we can ensure we have correct newlines
    temp_file = ensure_nl2br(md_file_path)
    page, meta = _build(temp_file, static_folder / assets_folder, MKDOCS_CONFIG, template=template,
                        generate_static_files=generate_static_files)
    temp_file.unlink()

    page = page.replace('../assets/', {True: f'/{static_folder}/{assets_folder}/',
                                       False: f'../{static_folder}/{assets_folder}/'}[abspath])

    if include_metadata:
        return page, meta
    return page


def mdfile_to_sections(md_file_path: Path, static_folder: Path = Path('static'),
                       assets_folder: Path = Path('turtleconvert'), remove_heading: bool = True,
                       abspath: bool = True, template: Path = 'turtleconvert.html',
                       generate_static_files: bool = False) -> dict:
    """Returns a dictionary of HTML content divided into sections.
    {
        "heading": "My Markdown File!",
        "head": "<Everything inside of the head tag>",
        "body": "<Everything inside of the body tag (excluding the heading unless remove_heading=False)>",
        "meta": { <All the metadata (frontmatter) from the markdown file as a dictionary> }
    }
    """
    md_file_path, static_folder, assets_folder = _str_to_path_mass_convert([md_file_path, static_folder, assets_folder])

    page, meta = mdfile_to_html(md_file_path, static_folder, assets_folder, include_metadata=True, abspath=abspath,
                                template=template, generate_static_files=generate_static_files)

    head_and_body = re.findall(r"<head.*?>(.*?)</head>.*?<body.*?>(.*?)</body>", page, re.DOTALL)

    head = head_and_body[0][0]
    body = head_and_body[0][1]
    h1_tag = meta.get('title', re.search(r'<h1.*?\>(.+?)\<\/h1>', body).group(1))

    if remove_heading:
        body = re.sub(r'<h1.*?\>(.+?)\<\/h1>', '', body, count=1)

    return {
        'heading': h1_tag,
        'head': head,
        'body': body,
        'meta': meta
    }


if __name__ == '__main__':
    # Testing data, feel free to ignore this
    import timeit

    generate_static_files()
    print(mdfile_to_sections('test.md', template='../example_override.html'))

    start_time = timeit.default_timer()
    for _ in range(100):
        data = mdfile_to_html(Path('test.md'), abspath=False, template='../example_override.html')
    end_time = timeit.default_timer()
    delta = end_time - start_time
    print(f'{delta:.10f} x100')

    start_time = timeit.default_timer()
    data = mdfile_to_html(Path('test.md'), abspath=False, template='../example_override.html')
    end_time = timeit.default_timer()
    print(f'{end_time - start_time:.10f} x1')
    data = data.replace('Automatically generated',
                        f'Automatically generated (in {end_time - start_time:.3f} seconds, excluding static files, 100 iterations took {delta:.3f} seconds)')
    with open('static/test.html', 'w', encoding='utf-8') as f:
        f.write(data)

    # Import partial to create a custom function for sections using separate paths
    # from functools import partial
    #
    # my_partial_function = partial(mdfile_to_sections, static_folder=Path('a_different_static_folder'),
    #                               assets_folder=Path('a_different_assets_folder'))
    #
    # generate_static_files(Path('a_different_static_folder'), Path('a_different_assets_folder'))
    # result = my_partial_function('test.md')
    # print(result)
