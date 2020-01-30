from canonicalwebteam.templatefinder import TemplateFinder

from flask import Flask
from flask_testing import TestCase

import os


class TestTemplateFinder(TestCase):
    def create_app(self):
        app = Flask(
            __name__,
            template_folder=os.path.dirname(os.path.abspath(__file__))
            + "/fixtures",
        )

        app.config["TESTING"] = True

        template_finder_view = TemplateFinder.as_view("template_finder")
        app.add_url_rule("/", view_func=template_finder_view)
        app.add_url_rule("/<path:subpath>", view_func=template_finder_view)

        return app

    def test_getting_html(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"<h1>TEST</h1>")

    def test_getting_nested_html(self):
        response = self.client.get("/nested")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"<h1>NESTED HTML</h1>")

    def test_404_if_no_template_present(self):
        response = self.client.get("/does-not-exist")
        self.assertEqual(response.status_code, 404)

    def test_getting_markdown(self):
        response = self.client.get("/test")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            (
                b"<h1>MARKDOWN</h1>\n"
                b'<h1 id="this-is-a-markdown-heading">'
                b"This is a markdown heading</h1>"
            ),
        )

    def test_getting_nested_markdown(self):
        response = self.client.get("/nested/test")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            (
                b'<h1>MARKDOWN</h1>\n<h1 id="this-is-a-nested">'
                b"This is a nested</h1>"
            ),
        )

    def test_heading_id_with_special_chars(self):
        response = self.client.get("/special-chars-test")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            (
                b'<h1>MARKDOWN</h1>\n<h1 id="h1-with-special-chars">'
                b"<code>&lt;h1&gt;</code> with 'special' chars</h1>"
            ),
        )

    def test_get_markdown_with_missing_wrapper_metadata(self):
        response = self.client.get("/test-missing-wrapper")
        self.assertEqual(response.status_code, 404)

    def test_get_markdown_with_missing_wrapper_file(self):
        response = self.client.get("/test-missing-wrapper-file")
        self.assertEqual(response.status_code, 404)
