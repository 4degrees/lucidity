..
    :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
    :license: See LICENSE.txt.

.. _tutorial:

Tutorial
========

.. module:: lucidity

This tutorial gives a good introduction to using Lucidity.

First make sure that you have Lucidity :ref:`installed <installation>`.

Patterns
--------

Lucidity uses patterns to represent a path structure. A pattern is very much
like the format you would use in a Python string format expression.

For example, a pattern to represent this filepath::

    '/jobs/monty/assets/circus/model/high/circus_high_v001.abc'

Could be::

    '/jobs/{job}/assets/{asset_name}/model/{lod}/{asset_name}_{lod}_v{version}.{filetype}'

Each ``{name}`` in braces is a variable that can either be extracted from a
matching path, or substituted with a provided value when constructing a path.
The variable is referred to as a `placeholder`.

Templates
---------

A :py:class:`~lucidity.template.Template` is a simple container for a pattern.

First, import the package::

    >>> import lucidity
    
Now, construct a template with the pattern above::

    >>> template = lucidity.Template('model', '/jobs/{job}/assets/{asset_name}/model/{lod}/{asset_name}_{lod}_v{version}.{filetype}')

.. note::

    The template must be given a name to identify it. The name becomes useful
    when you have a bunch of templates to manage.

You can check the identified placeholders in a template using the
:py:meth:`Template.keys <lucidity.template.Template.keys>` method::

    >>> print template.keys()
    set(['job', 'asset_name', 'lod', 'version', 'filetype'])

Parsing
-------

With a template defined we can now parse a path and extract data from it::

    >>> path = '/jobs/monty/assets/circus/model/high/circus_high_v001.abc'
    >>> data = template.parse(path)
    >>> print data
    {
        'job': 'monty',
        'asset_name': 'circus',
        'lod': 'high',
        'version': '001',
        'filetype': 'abc'
    }

If a template's pattern does not match the path then
:py:meth:`~lucidity.template.Template.parse` will raise a
:py:class:`~lucidity.error.ParseError`::

    >>> print template.parse('/other/monty/assets')
    ParseError: Input '/other/monty/assets' did not match template pattern.

Handling Duplicate Placeholders
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is perfectly acceptable for a template to contain the same placeholder
multiple times, as seen in the template constructed above. When parsing, by
default, the last matching value for a placeholder is used::

    >>> path = '/jobs/monty/assets/circus/model/high/spaceship_high_v001.abc'
    >>> data = template.parse(path)
    >>> print data['asset_name']
    spaceship

This is called :attr:`~lucidity.template.Template.RELAXED` mode. If this
behaviour is not desirable then the *duplicate_placeholder_mode* of any
:class:`~lucidity.template.Template` can be set to
:attr:`~lucidity.template.Template.STRICT` mode instead::

    >>> path = '/jobs/monty/assets/circus/model/high/spaceship_high_v001.abc'
    >>> template.duplicate_placeholder_mode = template.STRICT
    >>> template.parse(path)
    ParseError: Different extracted values for placeholder 'asset_name' detected. Values were 'circus' and 'spaceship'.

.. note::

    *duplicate_placeholder_mode* can also be passed as an argument when
    constructing a template.

Anchoring
^^^^^^^^^

By default, a pattern is anchored at the start, requiring that the start of a
path match the pattern::

    >>> job_template = lucidity.Template('job', '/job/{job}')
    >>> print job_template.parse('/job/monty')
    {'job': 'monty'}
    >>> print job_template.parse('/job/monty/extra/path')
    {'job': 'monty'}
    >>> print job_template.parse('/other/job/monty')
    ParseError: Input '/other/job/monty' did not match template pattern.

The anchoring can be changed when constructing a template by passing an
*anchor* keyword in::

    >>> filename_template = lucidity.Template(
    ...     'filename',
    ...     '{filename}.{index}.{ext}',
    ...     anchor=lucidity.Template.ANCHOR_END
    ... )
    >>> print filename_template.parse('/some/path/to/file.0001.dpx')
    {'filename': 'file', 'index': '0001', 'ext': 'dpx'}

The anchor can be one of:

    * :attr:`~template.Template.ANCHOR_START` - Match pattern at the start
      of the string.
    * :attr:`~template.Template.ANCHOR_END` - Match pattern at the end of
      the string.
    * :attr:`~template.Template.ANCHOR_BOTH` - Match pattern exactly.
    * ``None`` - Match pattern once anywhere in the string.
    
Formatting
----------

It is also possible to pass a dictionary of data to a template in order to
produce a path::

    >>> data = {
    ...     'job': 'monty',
    ...     'asset_name': 'circus',
    ...     'lod': 'high',
    ...     'version': '001',
    ...     'filetype': 'abc'
    ... }
    >>> path = template.format(data)
    >>> print path
    /jobs/monty/assets/circus/model/high/circus_high_v001.abc

In the example above, we haven't done more than could be achieved with standard
Python string formatting. In the next sections, though, you will see the need
for a dedicated :py:meth:`~lucidity.template.Template.format` method.

If the supplied data does not contain enough information to fill the template
completely a :py:class:`~lucidity.error.FormatError` will be raised::

    >>> print template.format({})
    FormatError: Could not format data {} due to missing key 'job'.
    
Nested Data Structures
----------------------

Often the data structure you want to use will be more complex than a single
level dictionary. Therefore, Lucidity also supports nested dictionaries when
both parsing or formatting a path.

To indicate a nested structure, use a dotted notation in your placeholder
name::

    >>> template = lucidity.Template('job', '/jobs/{job.code}')
    >>> print template.parse('/jobs/monty')
    {'job': {'code': 'monty'}}
    >>> print template.format({'job': {'code': 'monty'}})
    /jobs/monty
    
.. note::

    Unlike the standard Python format syntax, the dotted notation in Lucidity
    always refers to a nested item structure rather than attribute access.

Custom Regular Expressions
--------------------------

Lucidity works by constucting a regular expression from a pattern. It replaces
all placeholders with a default regular expression that should suit most cases.

However, if you need to customise the regular expression you can do so either
at a template level or per placeholder.

At The Template Level
^^^^^^^^^^^^^^^^^^^^^

To modify the default regular expression for a template, pass it is as an
additional argument::

    >>> template = lucidity.Template('name', 'pattern',
                                     default_placeholder_expression='[^/]+')

Per Placeholder
^^^^^^^^^^^^^^^

To alter the expression for a single placeholder, use a colon ``:`` after the
placeholder name and follow with your custom expression::

    >>> template = lucidity.Template('name', 'file_v{version:\d+}.ext')
    
Above, the `version` placeholder expression has been customised to only match
one or more digits.

.. note::

    If your custom expression requires the use of braces (``{}``) you must
    escape them to distinguish them from the placeholder braces. Use a
    preceding backslash for the escape (``\{``, ``\}``).

And of course, any custom expression text is omitted when formatting data::

    >>> print template.format({'version': '001'})
    file_v001.ext
    