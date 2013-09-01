..
    :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
    :license: See LICENSE.txt.

.. _multiple_templates:

Managing Multiple Templates
===========================

.. module:: lucidity

Representing different path structures requires the use of multiple templates.

Lucidity provides a few helper functions for dealing with multiple templates.

Template Discovery
------------------

Templates can be *discovered* by searching a list of paths for 
:ref:`mount points <multiple_templates.mount_points>` that register template 
instances. By default, the list of paths is retrieved from the environment 
variable :envvar:`LUCIDITY_TEMPLATE_PATH`.

To search and load templates in this way::

     >>> import lucidity
     >>> templates = lucidity.discover_templates()

To specify a specific list of paths just pass them to the function::

     >>> templates = lucidity.discover_templates(paths=['/templates'])
     
By default each path will be recursively searched. You can disable this
behaviour by setting the ``recursive`` keyword argument::

     >>> templates = lucidity.discover_templates(recursive=False)

.. _multiple_templates.mount_points:

Template Mount Points
---------------------

To write a template mount point, define a Python file containing a ``register``
function. The function should return a list of instantiated 
:py:class:`~lucidity.template.Template` instances::

    # templates.py
    
    from lucidity import Template
    
    def register():
        '''Register templates.'''
        return [
            Template('job', '/jobs/{job.code}'),
            Template('shot', '/jobs/{job.code}/shots/{scene.code}_{shot.code}')
        ]

Place the file on one of the search paths for 
:py:func:`~lucidity.discover_templates` to have it take effect.

Operations Against Multiple Templates
-------------------------------------

Lucidity also provides two top level functions to run a 
:py:class:`~lucidity.parse` or :py:class:`~lucidity.format`
operation against multiple candidate templates using the first correct result
found.

Given the following templates::

    >>> import lucidity
    >>> templates = [
    ...     lucidity.Template('model', '/jobs/{job}/assets/model/{lod}'),
    ...     lucidity.Template('rig', '/jobs/{job}/assets/rig/{rig_type}')
    ... ]

To perform a parse::

    >>> print lucidity.parse('/jobs/monty/assets/rig/anim', templates)
    ({'job': 'monty', 'rig_type': 'anim'},
     Template(name='rig', pattern='/jobs/{job}/assets/rig/{rig_type}'))


To format data::

    >>> print lucidity.format({'job': 'monty', 'rig_type': 'anim'}, templates)
    ('/jobs/monty/assets/rig/anim',
     Template(name='rig', pattern='/jobs/{job}/assets/rig/{rig_type}'))

.. note::
    
    The return value is a tuple of ``(result, template)``.

If no template could provide a result an appropriate error is raised (
:py:class:`~lucidity.error.ParseError` or
:py:class:`~lucidity.error.FormatError`).

     