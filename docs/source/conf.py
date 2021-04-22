# -*- coding: utf-8 -*-
import sys
from pathlib import Path
import pydata_sphinx_theme
from empyrical import __version__ as version

sys.path.insert(0, Path("../..").resolve(strict=True).as_posix())


# This is the expected signature of the handler for this event, cf doc
def autodoc_skip_member_handler(app, what, name, obj, skip, options):
    # Basic approach; you might want a regex instead
    return name.startswith(("cache", "_"))


# Automatically called by sphinx at startup
def setup(app):
    # Connect the autodoc-skip-member event from apidoc to the callback
    app.connect("autodoc-skip-member", autodoc_skip_member_handler)


extensions = [
    "sphinx.ext.autodoc",
    "numpydoc",
    "m2r2",
    "sphinx_markdown_tables",
    "nbsphinx",
    "sphinx.ext.mathjax",
    "sphinx_copybutton",
]

templates_path = ["_templates"]

source_suffix = {".rst": "restructuredtext", ".md": "markdown"}

master_doc = "index"

project = "empyrical"
copyright = "2016, Quantopian, Inc."
author = "Quantopian, Inc."

release = version
language = None

exclude_patterns = []

highlight_language = "python"

pygments_style = "sphinx"

todo_include_todos = False

html_theme = "pydata_sphinx_theme"
html_theme_path = pydata_sphinx_theme.get_html_theme_path()

html_theme_options = {
    "github_url": "https://github.com/stefan-jansen/emyrical-reloaded",
    "twitter_url": "https://twitter.com/ml4trading",
    "external_links": [
        {"name": "ML for Trading", "url": "https://ml4trading.io"},
        {"name": "Community", "url": "https://exchange.ml4trading.io"},
    ],
    "google_analytics_id": "UA-74956955-3",
    "use_edit_page_button": True,
}

html_context = {
    "github_url": "https://github.com",
    "github_user": "stefan-jansen",
    "github_repo": "empyrical-reloaded",
    "github_version": "main",
    "doc_path": "docs/source",
}

html_static_path = []

htmlhelp_basename = "Empyricaldoc"

latex_elements = {}

latex_documents = [
    (
        master_doc,
        "Empyrical.tex",
        "Empyrical Documentation",
        "Quantopian, Inc.",
        "manual",
    )
]

man_pages = [(master_doc, "empyrical", "Empyrical Documentation", [author], 1)]

texinfo_documents = [
    (
        master_doc,
        "Empyrical",
        "Empyrical Documentation",
        author,
        "Empyrical",
        "One line description of project.",
        "Miscellaneous",
    )
]
