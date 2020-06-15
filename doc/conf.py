import os
import sys

sys.path.insert(0, os.path.abspath('..'))
from monetdbe.version import __version__

project = 'monetdbe'
copyright = '2020, Gijs Molenaar'
author = 'Gijs Molenaar'
release = __version__

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'

html_static_path = ['_static']
