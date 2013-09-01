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

Extracting Data From A Path
---------------------------

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

.. note::

    When a group name in a pattern occurs more than once (as with 
    ``{asset_name}`` and ``{lod}`` above), the last matching value is used for 
    the returned data.

If a template's pattern does not match the full path exactly then
:py:meth:`~lucidity.template.Template.parse` will raise a
:py:class:`~lucidity.error.ParseError`::

    >>> print template.parse('/jobs/monty/assets')
    ParseError: Input '/jobs/monty/assets' did not match template pattern.
    
Constructing A Path From Data
-----------------------------

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
    