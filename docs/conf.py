# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
# set the correct path for the imports
sys.path.insert(0, os.path.abspath("../.."))

project = 'Heisenware Native Agent Packager'
copyright = '2025, Heisenware'
author = 'Dovydas Girdvainis'
release = '2025'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_rtd_theme',
    'sphinx.ext.viewcode',
    'sphinx.ext.autodoc',
    'sphinx.ext.githubpages'
]

templates_path = ['_templates']
exclude_patterns = ["build"]

autodoc_default_options = {
    'members': True,
    'private-members': True
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_show_sourcelink = False
html_static_path = ['_static']
