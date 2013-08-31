..
    :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
    :license: See LICENSE.txt.

.. _introduction:

Introduction
============

Lucidity is a framework for templating filesystem structure.

It works using regular expressions, but hides much of the verbosity through
the use of simple placeholders (such as you see in Python string formatting).

Consider the following paths::

    /jobs/monty/assets/circus/model/high/circus_high_v001.abc
    /jobs/monty/assets/circus/model/low/circus_low_v001.abc
    /jobs/monty/assets/parrot/model/high/parrot_high_v002.abc
    
A regular expression to describe them might be::

    '/jobs/(?P<job>[\w_]+?)/assets/(?P<asset_name>[\w_]+?)/model/(?P<lod>[\w_]+?)/(?P<asset_name>[\w_]+?)_(?P<lod>[\w_]+?)_v(?P<version>\d+?)\.(?P<filetype>\w+?)'

Meanwhile, the Lucidity pattern would be::

    '/jobs/{job}/assets/{asset_name}/model/{lod}/{asset_name}_{lod}_v{version}.{filetype}'

With Lucidity you store this pattern as a template and can then use that
template to generate paths from data as well as extract data from matching
paths in a standard fashion.

Read the :ref:`tutorial` to find out more.

Copyright & License
-------------------

Copyright (c) 2013 Martin Pengelly-Phillips

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this work except in compliance with the License. You may obtain a copy of the
License in the LICENSE.txt file, or at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

