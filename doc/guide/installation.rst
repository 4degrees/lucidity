..
    :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
    :license: See LICENSE.txt.

.. _installation:

Installation
============

.. highlight:: bash

Installing Lucidity is simple with `pip <http://www.pip-installer.org/>`_::

    $ pip install lucidity

If the Cheeseshop (a.k.a. PyPI) is down, you can also install Lucidity from one
of the mirrors::

    $ pip install --use-mirrors lucidity

Alternatively, you may wish to download manually from Github where Lucidity
is `actively developed <https://github.com/4degrees/lucidity>`_.

You can clone the public repository::

    $ git clone git://github.com/4degrees/lucidity.git

Or download an appropriate
`tarball <https://github.com/4degrees/lucidity/tarball/master>`_ or
`zipball <https://github.com/4degrees/lucidity/zipball/master>`_

Once you have a copy of the source, you can embed it in your Python package,
or install it into your site-packages::

    $ python setup.py install

Dependencies
------------

* `Python <http://python.org>`_ >= 2.6, < 3
* `Bunch <https://github.com/dsc/bunch>`_ >= 1.0.1

For testing:

* `Pytest <http://pytest.org>`_  >= 2.3.5
