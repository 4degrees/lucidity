# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

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


setup(
    name='Lucidity',
    version='1.0.0dev',
    description='Filesystem templating and management.',
    packages=[
        'lucidity',
    ],
    package_dir={
        '': 'source'
    },
    author='Martin Pengelly-Phillips',
    author_email='martin@4degrees.ltd.uk',
    license='Apache License (2.0)',
    long_description=open('README.rst').read(),
    url='https://github.com/4degrees/lucidity',
    keywords='filesystem, management, templating',
    tests_require=['pytest'],
    cmdclass={
        'test': PyTest
    }
)

