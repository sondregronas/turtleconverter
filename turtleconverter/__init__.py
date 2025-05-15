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
    return [
        Path(value) if isinstance(value, str) else value for value in list_of_values
    ]


def generate_static_files(
        static_folder: Path = Path("static"), assets_folder: Path = Path("turtleconvert")
) -> None:
    """Generates the static files for the HTML file."""
    static_folder, assets_folder = _str_to_path_mass_convert(
        [static_folder, assets_folder]
    )
    _build(None, static_folder / assets_folder, MKDOCS_CONFIG, only_static_files=True)


# If we only have a single newline after ``` or |, add a second \n
newline_blockers = [r"```"]
except_on = ["\n", r"(?:[^\S\r\n]*>)", r"[^\S\r\n]+\n"]
callouts_group = r"(?:[^\S\r\n]*>)*"
newline_regex = re.compile(
    rf'({"|".join(newline_blockers)})\n({callouts_group})(?!{"|".join(except_on)})'
)


def ensure_nl2br_katex(content: str) -> str:
    """Ensure that there are newlines after katex blocks, especially in callout blocks"""
    new_content = ""
    leading_callouts = ""
    in_katex, just_exited_katex = False, False
    for line in content.split("\n"):
        if just_exited_katex and not re.match(r"([^\S\r\n]*>?)*\n", line):
            new_content += f"{leading_callouts}\n"
            just_exited_katex = False

        if line.endswith("$$"):
            in_katex = not in_katex
            leading_callouts = re.match(r"((?:[^\S\r\n]*>?)*)", line).group(0)
            if not in_katex:
                just_exited_katex = True

        new_content += f"{line}\n"

    return new_content


regex_form_normal = re.compile(r"(\|)\n(?![^\S\r\n]*>)(?![^\S\r\n]*\|)")
regex_form_callouts = re.compile(r"(\|)\n((?:[^\S\r\n]*>)+)(?![^\S\r\n]*\|)")


def ensure_nl2br_forms(content: str) -> str:
    content = regex_form_normal.sub(r"\1\n\n", content)
    return regex_form_callouts.sub(r"\1\n\2\n\2", content)


def ensure_nl2br(md_file_path: Path) -> Path:
    """Ensures that all newlines in a markdown file are converted to <br> tags."""
    # Create a temporary file in memory to store the new content
    # The file will be deleted after the function is done
    with open(md_file_path, "r", encoding="utf-8") as f:
        content = f.read()
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as f:
        matches = newline_regex.findall(content)

        for match in matches:
            # If group 2 matches, add it along with the newline
            if match[1]:
                content = content.replace(f"{match[0]}\n", f"{match[0]}\n{match[1]}\n")
        content = newline_regex.sub(r"\1\n\n", content)
        content = ensure_nl2br_katex(content)
        content = ensure_nl2br_forms(content)

        f.write(content)
    return Path(f.name)


def mdfile_to_html(
        md_file_path: Path,
        static_folder: Path = Path("static"),
        assets_folder: Path = Path("turtleconvert"),
        include_metadata: bool = False,
        abspath: bool = True,
        template: Path = "turtleconvert.html",
        generate_static_files: bool = False,
) -> str or tuple:
    """Converts a markdown file to a html file."""
    md_file_path, static_folder, assets_folder = _str_to_path_mass_convert(
        [md_file_path, static_folder, assets_folder]
    )
    # Create a temporary file to store the new content so we can ensure we have correct newlines
    temp_file = ensure_nl2br(md_file_path)
    page, meta = _build(
        temp_file,
        static_folder / assets_folder,
        MKDOCS_CONFIG,
        template=template,
        generate_static_files=generate_static_files,
    )
    temp_file.unlink()

    page = page.replace(
        "../assets/",
        {
            True: f"/{static_folder}/{assets_folder}/",
            False: f"../{static_folder}/{assets_folder}/",
        }[abspath],
    )

    if include_metadata:
        return page, meta
    return page


def mdfile_to_sections(
        md_file_path: Path,
        static_folder: Path = Path("static"),
        assets_folder: Path = Path("turtleconvert"),
        remove_heading: bool = True,
        abspath: bool = True,
        template: Path = "turtleconvert.html",
        generate_static_files: bool = False,
) -> dict:
    """Returns a dictionary of HTML content divided into sections.
    {
        "heading": "My Markdown File!",
        "head": "<Everything inside of the head tag>",
        "body": "<Everything inside of the body tag (excluding the heading unless remove_heading=False)>",
        "meta": { <All the metadata (frontmatter) from the markdown file as a dictionary> }
    }
    """
    md_file_path, static_folder, assets_folder = _str_to_path_mass_convert(
        [md_file_path, static_folder, assets_folder]
    )

    page, meta = mdfile_to_html(
        md_file_path,
        static_folder,
        assets_folder,
        include_metadata=True,
        abspath=abspath,
        template=template,
        generate_static_files=generate_static_files,
    )

    head_and_body = re.findall(
        r"<head.*?>(.*?)</head>.*?<body.*?>(.*?)</body>", page, re.DOTALL
    )

    head = head_and_body[0][0]
    body = head_and_body[0][1]
    h1_tag = meta.get("title", re.search(r"<h1.*?\>(.+?)\<\/h1>", body).group(1))

    if remove_heading:
        body = re.sub(r"<h1.*?\>(.+?)\<\/h1>", "", body, count=1)

    if not "title" in meta:
        meta["title"] = h1_tag

    return {"heading": h1_tag, "head": head, "body": body, "meta": meta}


if __name__ == "__main__":
    # Testing data, feel free to ignore this
    import timeit

    generate_static_files()
    print(mdfile_to_sections("test.md", template="../example_override.html"))

    start_time = timeit.default_timer()
    for _ in range(100):
        data = mdfile_to_html(
            Path("test.md"), abspath=False, template="../example_override.html"
        )
    end_time = timeit.default_timer()
    delta = end_time - start_time
    print(f"{delta:.10f} x100")

    start_time = timeit.default_timer()
    data = mdfile_to_html(
        Path("test.md"), abspath=False, template="../example_override.html"
    )
    end_time = timeit.default_timer()
    print(f"{end_time - start_time:.10f} x1")
    data = data.replace(
        "Automatically generated",
        f"Automatically generated (in {end_time - start_time:.3f} seconds, excluding static files, 100 iterations took {delta:.3f} seconds)",
    )
    with open("static/test.html", "w", encoding="utf-8") as f:
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
