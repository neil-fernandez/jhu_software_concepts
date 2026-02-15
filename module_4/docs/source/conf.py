import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))

project = "module_4 assignment"
copyright = "2026, Neil Fernandez"
author = "Neil Fernandez"
release = "0.1"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = []

autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
