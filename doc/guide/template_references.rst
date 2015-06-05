..
    :copyright: Copyright (c) 2015 Martin Pengelly-Phillips
    :license: See LICENSE.txt.

.. _template_references:

Using Template References
=========================

.. module:: lucidity.template

When the same pattern is used repetitively in several templates, it can be
useful to extract it out into a separate template that can be referenced.

To reference another template, use its name prefixed by the *at* symbol, @,  in
a placeholder::

    >>> shot_path = lucidity.Template('shot_path', '{@job_path}/shots/{shot.code}')

Template references are resolved on demand when performing operations with the
template, such as calling :meth:`Template.parse` or :meth:`Template.format`.
This is why the above didn't produce an error even though no *job_path* template
has been defined (or a way to lookup that template by name even). This
behaviour allows :ref:`discovery <multiple_templates/discovery>` of templates
without worrying about the order of template construction.

As soon as you attempt to perform an operation on the template that does require
resolving references, errors will be raised accordingly. For example, try
calling the :meth:`Template.keys` method::

    >>> print shot_path.keys()
    ResolveError: Failed to resolve reference 'job_path' as no template resolver set.

The error indicates that we have not provided the template with a way to
actually resolve template references. To do this we need to set the
*template_resolver* attribute on the template to an object that matches the
:class:`Resolver` interface. Fortunately, the resolver interface is simple so
a even a basic dictionary can act as a resolver::

    >>> resolver = {}
    >>> shot_path.template_resolver = resolver

.. note::

    The template resolver can also be passed as an argument when instantiating a
    new :class:`Template`.

Try getting the keys again::

    >>> print shot_path.keys()
    ResolveError: Failed to resolve reference 'job_path' using template resolver.

Slightly better. Now we have a resolver in place we just need to add the other
template to the resolver so that it can be looked up by name::

    >>> job_path = lucidity.Template('job_path', '/jobs/{job.code}')
    >>> resolver[job_path.name] = job_path

.. note::

    In a future release a dedicated template collection class will make dealing
    with template references even easier.

Print the keys again and it should resolve all the references and give back the
full list of keys that make up the expanded template::

    >>> print shot_path.keys()
    set(['job.code', 'shot.code'])

There is also a method for listing the references found in a template::

    >>> print shot_path.references()
    set(['job_path'])

Additionally, if you would like to see the fully expanded pattern you can
manually call the :meth:`Template.expanded_pattern` method at any time::

    >>> print shot_path.expanded_pattern()
    /jobs/{job.code}/shots/{shot.code}

Anchor behaviour
----------------

A :class:`Template` has an :ref:`anchor <tutorial/anchoring>` setting that
determines how the template pattern is matched when parsing. When a template is
referenced in another template its anchor setting is ignored and only the anchor
setting of the outermost template is used:

    >>> template_a = lucidity.Template(
    ...     'a', 'path/{variable}', anchor=lucidity.Template.ANCHOR_START
    ... )
    >>> print template_a.parse('/some/path/value')
    ParseError: Path '/some/path/value' did not match template pattern.
    >>> resolver = {}
    >>> resolver[template_a.name] = template_a
    >>> template_b = lucidity.Template(
    ...     'b', '{@a}', anchor=lucidity.Template.ANCHOR_END,
    ...     template_resolver=resolver
    ... )
    >>> print template_b.parse('/some/path/value')
    {'variable': 'value'}
