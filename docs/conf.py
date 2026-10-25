"""Sphinx configuration for the TechArena Career Survival Agent docs."""

import sys
import tomllib
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DOCS_DIR.parent
PYPROJECT_TOML_PATH = PROJECT_ROOT / "pyproject.toml"

sys.path.insert(0, str(PROJECT_ROOT))

with PYPROJECT_TOML_PATH.open("rb") as pyproject_file:
    PROJECT_METADATA = tomllib.load(pyproject_file)

project = "TechArena: Career Survival Agent"
author = "TechArena Authors"
copyright = "2026, TechArena Authors"
version = release = PROJECT_METADATA["project"]["version"]

extensions = [
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_title = "TechArena — Career Survival Agent"

html_theme_options = {
    "style_external_links": True,
    "navigation_depth": 3,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "prev_next_buttons_location": "both",
}

language = "en"
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
