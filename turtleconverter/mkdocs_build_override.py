"""
This is a messy hack to override the mkdocs build command to convert a single markdown file to a html file.
"""

from __future__ import annotations

from pathlib import Path

import mkdocs.config
from mkdocs.commands.build import *
from mkdocs.commands.build import _populate_page, _build_page, _build_extra_template

if not os.path.exists(Path(__file__).parent / 'docs'):
    os.makedirs(Path(__file__).parent / 'docs')
MKDOCS_CONFIG = mkdocs.config.load_config(str(Path(__file__).parent / 'mkdocs.yml'))
if not os.listdir(Path(__file__).parent / 'docs'):
    os.rmdir(Path(__file__).parent / 'docs')


def _build_page(
        page: Page,
        config: MkDocsConfig,
        doc_files: Sequence[File],
        nav: Navigation,
        env: jinja2.Environment,
        dirty: bool = False,
        excluded: bool = False,
) -> None:
    """Pass a Page to theme template and write output to site_dir."""
    config._current_page = page
    try:
        # When --dirty is used, only build the page if the file has been modified since the
        # previous build of the output.
        if dirty and not page.file.is_modified():
            return

        log.debug(f"Building page {page.file.src_uri}")

        # Activate page. Signals to theme that this is the current page.
        page.active = True

        context = get_context(nav, doc_files, config, page)

        # Allow 'template:' override in md source files.
        template = env.get_template(page.meta.get('template', 'main.html'))

        # Run `page_context` plugin events.
        context = config.plugins.on_page_context(context, page=page, config=config, nav=nav)

        if excluded:
            page.content = (
                    '<div class="mkdocs-draft-marker" title="This page will not be included into the built site.">'
                    'DRAFT'
                    '</div>' + (page.content or '')
            )

        # Render the template.
        output = template.render(context)

        # Run `post_page` plugin events.
        output = config.plugins.on_post_page(output, page=page, config=config)

        return output

    except Exception as e:
        message = f"Error building page '{page.file.src_uri}':"
        # Prevent duplicated the error message because it will be printed immediately afterwards.
        if not isinstance(e, BuildError):
            message += f" {e}"
        log.error(message)
        raise
    finally:
        # Deactivate page
        page.active = False
        config._current_page = None


def _build(fp: Path, static_folder: Path = 'static', config: MkDocsConfig = MKDOCS_CONFIG, *,
           serve_url: str | None = None, dirty: bool = False) -> str:
    """Perform a full site build."""
    logger = logging.getLogger('mkdocs')

    # Add CountHandler for strict mode
    warning_counter = utils.CountHandler()
    warning_counter.setLevel(logging.WARNING)
    if config.strict:
        logging.getLogger('mkdocs').addHandler(warning_counter)

    inclusion = InclusionLevel.is_in_serve if serve_url else InclusionLevel.is_included

    try:
        # start = time.monotonic()

        # Run `config` plugin events.
        config = config.plugins.on_config(config)

        # if the docs folder doesn't exist, create it (it's required regardless of the build mode)

        # Run `pre_build` plugin events.
        config.plugins.on_pre_build(config=config)

        if not dirty:
            log.info("Cleaning site directory")
            utils.clean_directory(config.site_dir)
        else:  # pragma: no cover
            # Warn user about problems that may occur with --dirty option
            log.warning(
                "A 'dirty' build is being performed, this will likely lead to inaccurate navigation and other"
                " links within your site. This option is designed for site development purposes only."
            )

        if not serve_url:  # pragma: no cover
            log.info(f"Building documentation to directory: {config.site_dir}")
            if dirty and site_directory_contains_stale_files(config.site_dir):
                log.info("The directory contains stale files. Use --clean to remove them.")

        # First gather all data from all files/pages to ensure all data is consistent across all pages.
        files = get_files(config)

        # Inject the file into the files list
        injected_file = File(fp.name, src_dir=str(fp.parent.resolve()), dest_dir=config.site_dir,
                             use_directory_urls=config.use_directory_urls, dest_uri=f"{fp.stem}/index.html",
                             inclusion=InclusionLevel.INCLUDED)
        files.append(injected_file)

        env = config.theme.get_env()
        files.add_files_from_theme(env, config)

        # Run `files` plugin events.
        files = config.plugins.on_files(files, config=config)
        # If plugins have added files but haven't set their inclusion level, calculate it again.
        set_exclusions(files, config)

        nav = get_navigation(files, config)

        # Run `nav` plugin events.
        nav = config.plugins.on_nav(nav, config=config, files=files)

        log.debug("Reading markdown pages.")
        excluded = []
        for file in files.documentation_pages(inclusion=inclusion):
            log.debug(f"Reading: {file.src_uri}")
            if serve_url and file.inclusion.is_excluded():
                excluded.append(urljoin(serve_url, file.url))
            Page(None, file, config)
            assert file.page is not None
            mkdocs.commands.build._populate_page(file.page, config, files, dirty)
        if excluded:
            log.info(
                "The following pages are being built only for the preview "
                "but will be excluded from `mkdocs build` per `draft_docs` config:\n  - "
                + "\n  - ".join(excluded)
            )

        # Run `env` plugin events.
        env = config.plugins.on_env(env, config=config, files=files)

        ### Remove favicon, and replace the static folder with the new one
        log.debug("Copying static assets.")
        for file in files:
            file.dest_dir = static_folder.resolve()
            if file.src_uri == 'assets/images/favicon.png':
                file.inclusion = InclusionLevel.EXCLUDED
            file.dest_uri = file.dest_uri.replace('assets/', '')

        files.copy_static_files(dirty=dirty, inclusion=inclusion)

        # Generates sitemap and 404, etc.
        # for template in config.theme.static_templates:
        #    _build_theme_template(template, env, files, config, nav)

        for template in config.extra_templates:
            _build_extra_template(template, files, config, nav)

        doc_files = files.documentation_pages(inclusion=inclusion)
        assert doc_files[0].page is not None

        return _build_page(
            doc_files[0].page, config, doc_files, nav, env, dirty, excluded=file.inclusion.is_excluded()
        )

    except Exception as e:
        # Run `build_error` plugin events.
        config.plugins.on_build_error(error=e)
        if isinstance(e, BuildError):
            log.error(str(e))
            raise Abort('Aborted with a BuildError!')
        raise

    finally:
        logger.removeHandler(warning_counter)
