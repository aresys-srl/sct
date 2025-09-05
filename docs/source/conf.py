# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

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
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# If your documentation needs a minimal Sphinx version, state it here.
#
needs_sphinx = "7.2"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
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

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "**.ipynb_checkpoints"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"

html_theme_options = {
    #   "logo": {
    #       "image_light": "numpylogo.svg",
    #       "image_dark": "numpylogo_dark.svg",
    #   },
    "github_url": "https://github.com/aresys-srl/sct",
    # "collapse_navigation": True,
    # "external_links": [
    #     {"name": "Learn", "url": "https://numpy.org/numpy-tutorials/"},
    #     {"name": "NEPs", "url": "https://numpy.org/neps"},
    # ],
    # Add light/dark mode and documentation version switcher:
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
}

html_title = project
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}

html_copy_source = False

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "SCTDoc"

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
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
