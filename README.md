# TurtleConverter

A slow and inefficient converter for markdown to HTML. This is a very hacky way to use mkdocs to convert markdown files
to HTML. It works by overriding the build function of mkdocs to hook in a markdown file, and then extract the HTML from
the markdown file.

## Installation

```bash
pip install git+https://github.com/sondregronas/turtleconverter@main
```

## Usage

```py
from turtleconverter import mdfile_to_sections, mdfile_to_html


def mdfile_to_html(md_file_path: Path, static_folder: Path = Path('static'),
                   assets_folder: Path = 'turtleconvert') -> str:


# Convert markdown file to HTML
html = mdfile_to_html("test.md")
print(html)
# A complete HTML file with the contents of the markdown file
# Also generates a static/turtleconvert/ folder with the necessary assets (javascripts, stylesheets, css)

# def mdfile_to_sections(md_file_path: Path, static_folder: Path = Path('static'),
#                        assets_folder: Path = 'turtleconvert', isolate_heading: bool = True) -> dict:

# Convert markdown file to sections
sections = mdfile_to_sections("test.md")
print(sections)
# {
#    "heading": "My Markdown File!",
#    "head": "<Everything inside of the head tag>",
#    "body": "<Everything inside of the body tag (excluding the heading)>"
# }
# Also generates a static/turtleconvert/ folder with the necessary assets (javascripts, stylesheets, css)
```

Sections is useful if you want to include the markdown file in a template, and want to separate the head and body of the
file.

## Issues

- Images require a workaround