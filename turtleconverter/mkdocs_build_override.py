"""
This is a messy hack to override the mkdocs build command to convert a single markdown file to a html file.
"""

from __future__ import annotations
import fnmatch
import mkdocs.config
from mkdocs.commands.build import *
from mkdocs.commands.build import _build_page, _populate_page
from pathlib import Path

if not os.path.exists(Path(__file__).parent / "docs"):
    os.makedirs(Path(__file__).parent / "docs")
MKDOCS_CONFIG = mkdocs.config.load_config(str(Path(__file__).parent / "mkdocs.yml"))

# Document variables, these normally get set in the build command.
# Storing them here allows us to reuse the build command without having to set them again. (which is slow)
__logger = logging.getLogger("mkdocs")
__logger.setLevel(logging.ERROR)
__inclusion = InclusionLevel.is_included
__config = MKDOCS_CONFIG.plugins.on_config(MKDOCS_CONFIG)
__config.plugins.on_pre_build(config=__config)
utils.clean_directory(__config.site_dir)
__files = get_files(__config)
__env = __config.theme.get_env()
__files.add_files_from_theme(__env, __config)
__files = __config.plugins.on_files(__files, config=__config)
set_exclusions(__files, __config)
__nav = None
__nav = __config.plugins.on_nav(__nav, config=__config, files=__files)
__env = __config.plugins.on_env(__env, config=__config, files=__files)


class ConversionError(Exception):
    """Raised when an error occurs during the build process."""

    def __init__(self, message: str):
        super().__init__(message)


def _build_page(
    page: Page,
    config: MkDocsConfig,
    doc_files: Sequence[File],
    nav: Navigation,
    env: jinja2.Environment,
    template: str = "turtleconvert.html",
) -> tuple[str, any]:
    """Pass a Page to theme template and write output to site_dir."""
    try:
        context = get_context(nav, doc_files, config, page)

        if template != "turtleconvert.html":
            if not isinstance(template, Path):
                template = Path(template)
            # The path must be absolute from the cwd.
            template_path = template.resolve()

            # Write a file to the overrides folder called "custom_template.html" with the contents of the custom template
            # this is required because the template must be in the same directory as the mkdocs.yml file :(
            with open(
                Path(__file__).parent / "overrides" / "custom_template.html", "w+"
            ) as f:
                f.write(template_path.read_text())

            template = env.get_template("custom_template.html")
        else:
            template = env.get_template("turtleconvert.html")

        # Run `page_context` plugin events.
        context = config.plugins.on_page_context(
            context, page=page, config=config, nav=nav
        )

        # Render the template.
        output = template.render(context)

        # Run `post_page` plugin events.
        output = config.plugins.on_post_page(output, page=page, config=config)

        return output, page.meta

    except Exception as e:
        raise ConversionError(f"{e}")


# ---------------------------------------------------------------------------
# Roamlinks patch
# Roamlinks walks the filesystem directly (bypasses MkDocs Files), so we
# redirect its internal os.walk to a filtered version that respects ignore_glob.
# We also patch the replacer classes to produce absolute URLs via leading_url.
# ---------------------------------------------------------------------------
import re as _re
import mkdocs_roamlinks_plugin.plugin as _roam_plugin

_real_os_walk = os.walk  # captured before patching to avoid infinite recursion

# Active settings – set by _build() before each page render.
_active_ignore_glob: tuple[str, ...] = ()
_active_leading_url: str = "/"


def _roam_walk_filtered(base_docs_url):
    """os.walk replacement for roamlinks that skips ignore_glob paths."""
    for root, dirs, files in _real_os_walk(base_docs_url, followlinks=True):
        rel_root = os.path.relpath(root, base_docs_url).replace(os.sep, "/")
        filtered = [
            name
            for name in files
            if not any(
                fnmatch.fnmatch("/" + (rel_root + "/" + name).lstrip("./"), p)
                for p in _active_ignore_glob
            )
        ]
        yield root, dirs, filtered


def _make_absolute(rel_url: str, page_url: str) -> str:
    """Convert a relative link URL to an absolute URL using _active_leading_url."""
    page_dir = os.path.dirname(page_url).replace("\\", "/")
    abs_path = (
        os.path.normpath(os.path.join(page_dir, rel_url)).replace("\\", "/").lstrip("/")
    )
    leading = _active_leading_url.rstrip("/")
    return f"{leading}/{abs_path}" if abs_path else f"{leading}/"


def _absolutify_markdown_link(md_link: str, page_url: str) -> str:
    """Rewrite relative URLs inside a markdown link string to absolute URLs."""

    def _fix(m):
        url = m.group(1) if m.group(1) is not None else m.group(2)
        bracketed = m.group(1) is not None
        if (
            url.startswith("#")
            or url.startswith("http://")
            or url.startswith("https://")
        ):
            return m.group(0)
        abs_url = _make_absolute(url, page_url)
        return f"(<{abs_url}>)" if bracketed else f"({abs_url})"

    return _re.sub(r"\(<([^>]+)>\)|\(([^)]+)\)", _fix, md_link)


class _AbsoluteRoamLinkReplacer(_roam_plugin.RoamLinkReplacer):
    def __call__(self, match):
        result = super().__call__(match)
        if _active_leading_url == "/":
            return result
        return _absolutify_markdown_link(result, self.page_url)


class _AbsoluteAutoLinkReplacer(_roam_plugin.AutoLinkReplacer):
    def __call__(self, match):
        result = super().__call__(match)
        if _active_leading_url == "/":
            return result
        return _absolutify_markdown_link(result, self.page_url)


_roam_plugin.os.walk = lambda path, **kw: _roam_walk_filtered(path)
_roam_plugin.RoamLinkReplacer = _AbsoluteRoamLinkReplacer
_roam_plugin.AutoLinkReplacer = _AbsoluteAutoLinkReplacer


def _build(
    fp: Path,
    static_folder: Path = "static",
    config: MkDocsConfig = MKDOCS_CONFIG,
    *,
    template: str = "turtleconvert.html",
    only_static_files: bool = False,
    generate_static_files: bool = False,
    docs_folder: Path = None,
    ignore_glob: tuple[str, ...] = ("*/translations/*",),
    leading_url: str = "/",
) -> tuple[str, dict] or None:
    if docs_folder:
        __config.docs_dir = str(docs_folder.resolve())
    try:
        if generate_static_files or only_static_files:
            for file in __files:
                file.dest_dir = static_folder.resolve()
                if file.src_uri == "assets/images/favicon.png":
                    file.inclusion = InclusionLevel.EXCLUDED
                file.dest_uri = file.dest_uri.replace("assets/", "")
            __files.copy_static_files(dirty=False, inclusion=__inclusion)
        if only_static_files:
            return

        file = File(
            fp.name,
            src_dir=str(fp.parent.resolve()),
            dest_dir=config.site_dir,
            use_directory_urls=config.use_directory_urls,
            dest_uri=f"{fp.stem}/index.html",
            inclusion=InclusionLevel.INCLUDED,
        )
        file.page = Page(None, file, config)
        # Set active ignore patterns so the roamlinks os.walk patch applies.
        global _active_ignore_glob, _active_leading_url
        _active_ignore_glob = tuple(ignore_glob)
        _active_leading_url = leading_url
        _populate_page(file.page, config, __files)

        return _build_page(file.page, config, [file], __nav, __env, template=template)

    except Exception as e:
        raise ConversionError(f"Error building page '{fp}': {e}")
