# TemplateFinder

`TemplateFinder` is an extension of `TemplateView` which attempts to
load the corresponding templates directly from URLs, without the need to
write a view for each URL.

It can load HTML templates directly, or parse Markdown files that
contain a "wrapper\_template" frontmatter key.

## Usage

To register the template finder in your Flask app you need to register the template folder in the application config, and specify which routes should be handled by it.
The following example will handle everything via the templatefinder:

```
from canonicalwebteam.templatefinder import TemplateFinder

TEMPLATE_FOLDER = 

app = Flask(
    template_folder="templates",
    static_folder="static",
)
app.config["TEMPLATE_FOLDER"] = "templates"

template_finder_view = TemplateFinder.as_view("template_finder")
app.add_url_rule("/", view_fun  c=template_finder_view)
app.add_url_rule("/<path:subpath>", view_func=template_finder_view)
```

## Template matching

The templatefinder can be used to automatically map `.html` and `.md` files to url on a website.
When included the finder will search for files at the given url in a specified template directory.

E.g. `localhost/pages/test` will look for the following files, in order:

- `$TEMPLATE_FOLDER/pages/test.html`
- `$TEMPLATE_FOLDER/pages/test/index.html`
- `$TEMPLATE_FOLDER/pages/test.md`
- `$TEMPLATE_FOLDER/pages/test/index.md`

## Markdown parsing

If the `TemplateFinder` encounters a Markdown file (ending `.md`) it
will look for the following keys in [YAML
frontmatter](https://jekyllrb.com/docs/front-matter/):

-   `wrapper_template` *mandatory*: (e.g.:
    `wrapper_template: includes/markdown-wrapper.html`) A path to an
    HTML template within which to place the parsed markdown content.
    This path must be relative to Flask's `template_folder` root.
-   `context` *optional*: (e.g.:
    `context: {title: "Welcome", description: "A welcome page"}`) A
    dictionary of extra key / value pairs to pass through to the
    template context.
-   `markdown_includes` *optional*: (e.g.: `markdown_includes: {nav: }`)
    A mapping of key names to template paths pointing to Markdown files
    to include. Each template path will be parsed, the resulting HTML
    will be passed in the template context, under the relevant key.
    Paths must be relative to Flask's `template_folder` root.

Here's an example Markdown file:

``` markdown
---
wrapper_template: "includes/markdown-wrapper.html"
markdown_includes:
  nav: "includes/nav.md"
context:
  title: "Welcome"
  description: "A welcome page"
---

Welcome to my website.

## GitHub

I also have [a GitHub page](https://github.com/me).
```

## Tests
Tests can be run with pytest:

``` bash
pip3 install -r requirements.txt
python3 -m pytest test
```
