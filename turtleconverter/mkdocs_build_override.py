"""
This is a messy hack to override the mkdocs build command to convert a single markdown file to a html file.
"""

from __future__ import annotations

from pathlib import Path

import mkdocs.config
from mkdocs.commands.build import *
from mkdocs.commands.build import _build_page, _build_extra_template, _populate_page

if not os.path.exists(Path(__file__).parent / 'docs'):
    os.makedirs(Path(__file__).parent / 'docs')
MKDOCS_CONFIG = mkdocs.config.load_config(str(Path(__file__).parent / 'mkdocs.yml'))


def _build_page(
        page: Page,
        config: MkDocsConfig,
        doc_files: Sequence[File],
        nav: Navigation,
        env: jinja2.Environment,
        template: str = 'turtleconvert.html',
) -> tuple[str, any]:
    """Pass a Page to theme template and write output to site_dir."""
    config._current_page = page
    try:
        log.debug(f"Building page {page.file.src_uri}")

        # Activate page. Signals to theme that this is the current page.
        page.active = True

        context = get_context(nav, doc_files, config, page)

        if template != 'turtleconvert.html':
            if not isinstance(template, Path):
                template = Path(template)
            # The path must be absolute from the cwd.
            template_path = template.resolve()

            # Write a file to the overrides folder called "custom_template.html" with the contents of the custom template
            with open(Path(__file__).parent / 'overrides' / 'custom_template.html', 'w+') as f:
                f.write(template_path.read_text())

            template = env.get_template('custom_template.html')
        else:
            template = env.get_template('turtleconvert.html')

        # Run `page_context` plugin events.
        context = config.plugins.on_page_context(context, page=page, config=config, nav=nav)

        # Render the template.
        output = template.render(context)

        # Run `post_page` plugin events.
        output = config.plugins.on_post_page(output, page=page, config=config)

        return output, page.meta

    except Exception as e:
        message = f"Error building page '{page.file.src_uri}':"
        # Prevent duplicated the error message because it will be printed immediately afterwards.
        if not isinstance(e, BuildError):
            message += f" {e}"
        log.error(message)
        raise


def _build(fp: Path, static_folder: Path = 'static', config: MkDocsConfig = MKDOCS_CONFIG, *,
           template: str = 'turtleconvert.html', only_static_files: bool = False,
           generate_static_files: bool = False) -> tuple[str, dict] or None:
    """Perform a full site build."""
    logger = logging.getLogger('mkdocs')

    # Add CountHandler for strict mode
    warning_counter = utils.CountHandler()
    warning_counter.setLevel(logging.WARNING)
    if config.strict:
        logging.getLogger('mkdocs').addHandler(warning_counter)

    inclusion = InclusionLevel.is_included

    try:
        # Run `config` plugin events.
        config = config.plugins.on_config(config)

        # if the docs folder doesn't exist, create it (it's required regardless of the build mode)

        # Run `pre_build` plugin events.
        config.plugins.on_pre_build(config=config)

        utils.clean_directory(config.site_dir)

        # First gather all data from all files/pages to ensure all data is consistent across all pages.
        files = get_files(config)

        if not only_static_files:
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
        for file in files.documentation_pages(inclusion=inclusion):
            log.debug(f"Reading: {file.src_uri}")
            Page(None, file, config)
            assert file.page is not None
            _populate_page(file.page, config, files)

        # Run `env` plugin events.
        env = config.plugins.on_env(env, config=config, files=files)

        # Remove favicon, and replace the static folder with the new one
        log.debug("Copying static assets.")
        for file in files:
            file.dest_dir = static_folder.resolve()
            if file.src_uri == 'assets/images/favicon.png':
                file.inclusion = InclusionLevel.EXCLUDED
            file.dest_uri = file.dest_uri.replace('assets/', '')

        if generate_static_files or only_static_files:
            files.copy_static_files(dirty=False, inclusion=inclusion)
        if only_static_files:
            return

        # Generates sitemap and 404, etc.
        # for template in config.theme.static_templates:
        #    _build_theme_template(template, env, files, config, nav)

        for template in config.extra_templates:
            _build_extra_template(template, files, config, nav)

        doc_files = files.documentation_pages(inclusion=inclusion)
        assert doc_files[0].page is not None

        return _build_page(
            doc_files[0].page, config, doc_files, nav, env, template=template
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
