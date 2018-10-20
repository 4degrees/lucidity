..
    :copyright: Copyright (c) 2015 Martin Pengelly-Phillips
    :license: See LICENSE.txt.

.. _release/release_notes:

*************
Release Notes
*************

.. currentmodule:: lucidity.template

.. release:: Upcoming

    .. change:: fixed

        Specify dependencies using case sensitive names to support systems that
        cannot resolve in a case insensitive manner (such as `"Nexus Repository"
        <https://issues.sonatype.org/browse/NEXUS-12075>`__).

.. release:: 1.5.0
    :date: 2015-06-06

    .. change:: new

        Support for referencing a template in another template.

        .. seealso:: :ref:`template_references`

    .. change:: new

        Release notes in documentation using `Lowdown
        <http://lowdown.rtd.ftrack.com/en/latest/>`_.

.. release:: 1.4.1
    :date: 2015-05-26

    .. change:: changed

        Implemented custom formatter internally, removing dependency on Bunch
        and simplifying format logic.

.. release:: 1.4.0
    :date: 2015-05-25

    .. change:: new

        Added *duplicate_placeholder_mode* to control template behaviour when
        parsing templates with duplicate placeholders, including a new
        :attr:`~Template.STRICT` mode.

        .. seealso:: :ref:`tutorial/parsing/handling_duplicate_placeholders`

.. release:: 1.3.1
    :date: 2014-04-01

    .. change:: fixed

        :class:`Template` not deepcopyable.

.. release:: 1.3.0
    :date: 2014-03-28

    .. change:: changed

        Removed dependency on Regex module to simplify installation across
        different platforms.

.. release:: 1.2.0
    :date: 2014-03-09

    .. change:: new

        Added :meth:`Template.keys` for retrieving set of placeholders used
        in a template pattern.


.. release:: 1.1.0
    :date: 2014-03-08

    .. change:: new

        Support partial matching of template when parsing with the introduction
        of a new *anchor* setting on templates.

        .. seealso:: :ref:`tutorial/anchoring`

    .. change:: new

        Helper function :func:`lucidity.get_template` for retrieving a template
        by name from a list of templates.

    .. change:: fixed

        Special regex characters not escaped in pattern leading to incorrect
        parses.

    .. change:: fixed

        :meth:`Template.format` fails with unhandled :exc:`AttributeError` when
        nested dictionary is missing a required key.

.. release:: 1.0.0
    :date: 2013-09-01

    .. change::

        Initial release with support for :class:`Template` objects that can
        use a simple pattern to parse strings into data and format data into
        strings.

        .. seealso:: :ref:`tutorial`
