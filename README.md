# 🐢 TurtleConverter 🐢

[![GitHub Pages](https://badgen.net/badge/example%20output/github%20pages/?icon=chrome)](https://sondregronas.github.io/turtleconverter/)

A slow and inefficient converter for markdown to HTML. This is a very hacky way to use [mkdocs](https://www.mkdocs.org/)
to convert markdown files to HTML. It works by overriding the `_build` function of mkdocs to hook in a markdown file to
then extract the HTML from said markdown file. The header, nav and footer is omitted from the output.

## Installation

The package is not on PyPi, so you will have to install it from the git repository.

```bash
pip install git+https://github.com/sondregronas/turtleconverter@main
```

## Usage

```py
from turtleconverter import mdfile_to_sections, mdfile_to_html, generate_static_files

# def generate_static_files(static_folder: Path = Path('static'), assets_folder: Path = Path('turtleconvert')) -> None:
generate_static_files()
# Generates the static files (CSS, JS, etc.) in a "static/assets/" folder (paths must match with the other functions)


# def mdfile_to_html(md_file_path: Path, static_folder: Path = Path('static'),
#                    assets_folder: Path = Path('turtleconvert'), include_metadata: bool = False,
#                    abspath: bool = True, template: Path = 'turtleconvert.html',
#                    generate_static_files: bool = False) -> str or tuple:

# Converts a markdown file to HTML
html = mdfile_to_html("test.md")
print(html)
# A complete HTML file with the contents of the markdown file (note that the static files are not generated by default)
# The static folders / assets folders must match those used in the generate_static_files function


# def mdfile_to_sections(md_file_path: Path, static_folder: Path = Path('static'),
#                        assets_folder: Path = Path('turtleconvert'), remove_heading: bool = True,
#                        abspath: bool = True, template: Path = 'turtleconvert.html',
#                        generate_static_files: bool = False) -> dict:

# Converts a markdown file to sections
sections = mdfile_to_sections("test.md")
print(sections)
# {
#    "heading": "My Markdown File!",
#    "head": "<Everything inside of the head tag>",
#    "body": "<Everything inside of the body tag (excluding the heading unless remove_heading=False)>",
#    "meta": { <All the metadata (frontmatter) from the markdown file as a dictionary> }
# }
# The static folders / assets folders must match those used in the generate_static_files function
```

Sections is useful if you want to include the markdown file in a template, and want to separate the head and body of the
file.

You can also use the partial library to create your partial functions with different static folders for easier use

```py
from turtleconverter import mdfile_to_sections, generate_static_files
from functools import partial

my_partial_function = partial(mdfile_to_sections, static_folder=Path('a_different_static_folder'),
                              assets_folder=Path('a_different_assets_folder'))

generate_static_files(Path('a_different_static_folder'), Path('a_different_assets_folder'))
result = my_partial_function('test.md')
```

## Overrides folder

Feel free to fork & change the `overrides` folder or `mkdocs.yml` file to customize the template - you can add as many
mkdocs plugins as you want, as long as they are added to the pyproject.toml file before installing the package.

Note: the colors are defined in `overrides/base_turtleconvert.html` under the scripts section.

## Custom Template for HTML rendering

You may also pass a custom template to the renderer by passing them to the function as an argument like so:

```py
html = mdfile_to_html("test.md", template="custom_template.html")  # alternatively you can use a Path object
```

[example_override.html](example_override.html) is an example of a custom template that can be used during conversion, *
*<ins>though creating your own with jinja2 using the results from `mdfile_to_sections()` is the projects intended
usecase</ins>**. Note that mkdocs will always generate a h1 tag with the title of the markdown file, so you should not
include a h1 tag in your custom template.

## Issues

- Image paths remain relative to the markdown file - **this script does not move/copy any images!!**
- The converter only allows for one markdown file at a time, which is a _bit_ inefficient (but within the scope of the
  project)
