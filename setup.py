# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os
import re

from setuptools.command.test import test as TestCommand
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


class PyTest(TestCommand):
    '''Pytest command.'''

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        '''Import pytest and run.'''
        import pytest
        errno = pytest.main(self.test_args)
        raise SystemExit(errno)


with open(os.path.join(
    os.path.dirname(__file__), 'source', 'lucidity', '_version.py'
)) as _version_file:
    _version = re.match(
        r'.*__version__ = \'(.*?)\'', _version_file.read(), re.DOTALL
    ).group(1)


# Requirements.
setup_requires = [
    'Sphinx >= 1.3, < 2',
    'Lowdown >= 0.1.1, < 2'
]

install_requires = [

]

# Readthedocs requires Sphinx extensions to be specified as part of
# install_requires in order to build properly.
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if on_rtd:
    install_requires.extend(setup_requires)


setup(
    name='Lucidity',
    version=_version,
    description='Filesystem templating and management.',
    long_description=open('README.rst').read(),
    keywords='filesystem, management, templating',
    url='https://gitlab.com/4degrees/lucidity',
    author='Martin Pengelly-Phillips',
    author_email='martin@4degrees.ltd.uk',
    license='Apache License (2.0)',
    packages=[
        'lucidity',
    ],
    package_dir={
        '': 'source'
    },
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=[
        'pytest >= 2.3.5'
    ],
    cmdclass={
        'test': PyTest
    },
    zip_safe=False
)

