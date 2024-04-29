# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------

project = "SAR Calibration Toolbox (SCT)"
copyright = "2024, Aresys S.R.L."
author = "Aresys S.R.L."

import sct

SCT_VERSION = sct.__version__

# stripped version
stripped_version = SCT_VERSION[: SCT_VERSION[: SCT_VERSION.rfind(".")].rfind(".")]
# The full version, including alpha/beta/rc tags
release = SCT_VERSION

# -- General configuration ---------------------------------------------------

needs_sphinx = "7.2"
extensions = [
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.ifconfig",
    "sphinx.ext.napoleon",  # for numpy docstring
    "sphinx.ext.mathjax",
    "nbsphinx",
]
python_use_unqualified_type_names = True
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
exclude_patterns = ["_build", "**.ipynb_checkpoints"]
pygments_style = "sphinx"

# -- Options for HTML output -------------------------------------------------

html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "github_url": "https://github.com/aresys-srl/sct",
    "icon_links": [
        {
            "name": "Aresys",
            "url": "https://www.aresys.it/",
            "icon": "_static/icons/aresys_logo.svg",
            "type": "local",
        }
    ],
    # Add light/dark mode and documentation version switcher:
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
}
html_title = project
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_copy_source = False

# -- Options for HTMLHelp output ---------------------------------------------

htmlhelp_basename = "SCTDoc"

# -- Options for manual page output ------------------------------------------

man_pages = [(master_doc, "sct", "SAR Calibration Toolbox Documentation", [author], 1)]

# -- Extension configuration -------------------------------------------------

autodoc_default_options = {"members": True, "undoc-members": True}
autodoc_member_order = "bysource"  # alphabetical, groupwise
autoclass_content = "both"  # class, init, both
autodoc_preserve_defaults = True

autodoc_type_aliases = {"npt.ArrayLike": "ArrayLike"}

napoleon_use_param = True
napoleon_preprocess_types = True
napoleon_type_aliases = {}

# -- Options for intersphinx extension ---------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
}
