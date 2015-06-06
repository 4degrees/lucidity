# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

'''Lucidity documentation build configuration file'''

import os
import re

# -- General ------------------------------------------------------------------

# Extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'lowdown'
]

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'Lucidity'
copyright = u'2013, Martin Pengelly-Phillips'

# Version
with open(
    os.path.join(
        os.path.dirname(__file__), '..', 'source', 'lucidity', '_version.py'
    )
) as _version_file:
    _version = re.match(
        r'.*__version__ = \'(.*?)\'', _version_file.read(), re.DOTALL
    ).group(1)

version = _version
release = _version

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['static', 'template']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of prefixes to ignore for module listings
modindex_common_prefix = ['lucidity.']


# -- HTML output --------------------------------------------------------------

# If True, copy source rst files to output for reference
html_copy_source = True


# -- Autodoc ------------------------------------------------------------------

autodoc_default_flags = ['members', 'undoc-members', 'show-inheritance']
autodoc_member_order = 'bysource'

def autodoc_skip(app, what, name, obj, skip, options):
    '''Don't skip __init__ method for autodoc.'''
    if name == '__init__':
        return False

    return skip


# -- Intersphinx --------------------------------------------------------------

intersphinx_mapping = {'python':('http://docs.python.org/', None)}


# -- Setup --------------------------------------------------------------------

def setup(app):
    app.connect('autodoc-skip-member', autodoc_skip)

