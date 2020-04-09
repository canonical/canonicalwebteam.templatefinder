# Standard library
import os
import re

# Packages
import flask
from flask.views import View
from frontmatter import loads as load_frontmatter_from_markdown
from jinja2.exceptions import TemplateNotFound
from mistune import Markdown, BlockLexer, Renderer


class WebteamBlockLexer(BlockLexer):
    list_rules = (
        "newline",
        "block_code",
        "fences",
        "lheading",
        "hrule",
        "table",
        "nptable",
        "block_quote",
        "list_block",
        "block_html",
        "text",
    )


class IDRenderer(Renderer):
    def header(self, text, level, raw=None):
        header_id = (text.replace(" ", "-")).lower()
        header_id = re.sub(r"<[^<]+?>", "", header_id)
        header_id = re.sub(r"&[\w\d]+;", "", header_id)
        header_id = re.sub(r"[^\w-]", "", header_id)

        return f'<h{level} id="{header_id}">{text}</h{level}>'


class TemplateFinder(View):
    """
    A TemplateView that guesses the template name based on the
    url path
    """

    def __init__(self):
        self.markdown_parser = Markdown(
            block=WebteamBlockLexer(),
            renderer=IDRenderer(parse_block_html=True, parse_inline_html=True),
        )

    def dispatch_request(self, *args, **kwargs):
        """
        This is called when TemplateFinder is run as a view
        It tries to find the template for the request path
        and then passes that template name to TemplateView to render
        """
        path = flask.request.path.lstrip("/")
        matching_template = self._get_template(path)

        if not matching_template:
            flask.abort(404, f"Can't find page for: {path}")

        if matching_template[-2:] == "md":
            loader = flask.current_app.jinja_loader
            file_content = loader.get_source({}, template=matching_template)[0]
            parsed_file = load_frontmatter_from_markdown(file_content)
            wrapper_template = parsed_file.metadata.get("wrapper_template")

            if not (
                wrapper_template and self._template_exists(wrapper_template)
            ):
                return flask.abort(404, f"Can't find page for: {path}")

            # Get context from Flask, and update with context from frontmatter
            context = self._get_context()
            context.update(parsed_file.metadata.get("context", {}))

            # Add any Markdown includes to context
            # Make sure to run them through the template parser too
            for key, path in parsed_file.metadata.get(
                "markdown_includes", {}
            ).items():
                content = loader.get_source({}, template=path)[0]
                parsed_content = flask.render_template_string(
                    content, **context
                )
                context[key] = self.markdown_parser(parsed_content)

            # Parse the markdown
            parsed_content = flask.render_template_string(
                parsed_file.content, **context
            )
            context["content"] = self.markdown_parser(parsed_content)

            return flask.render_template(wrapper_template, **context)
        else:
            return flask.render_template(
                matching_template, **self._get_context()
            )

    def _get_context(self):
        context = {}
        clean_path = flask.request.path.strip("/")
        for index, path in enumerate(clean_path.split("/")):
            context["level_" + str(index + 1)] = path
        return context

    def _get_template(self, url_path):
        """
        Given a basic path, find an HTML or Markdown file
        """

        # If on part of the url has _ this means the accessed
        # file is a partial
        for url_part in url_path.split("/"):
            if url_part.startswith("_"):
                return None

        # Try to match HTML or Markdown files
        if self._template_exists(url_path + ".html"):
            return url_path + ".html"
        elif self._template_exists(os.path.join(url_path, "index.html")):
            return os.path.join(url_path, "index.html")
        elif self._template_exists(url_path + ".md"):
            return url_path + ".md"
        elif self._template_exists(os.path.join(url_path, "index.md")):
            return os.path.join(url_path, "index.md")

        return None

    def _template_exists(self, path):
        """
        Check if a template exists
        without raising an exception
        """
        loader = flask.current_app.jinja_loader
        try:
            loader.get_source({}, template=path)
        except TemplateNotFound:
            return False

        return True
