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
    version='0.1.0',
    description='Filesystem templating and management.',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
    ],
    keywords='filesystem, management, templating',
    url='https://github.com/4degrees/lucidity',
    author='Martin Pengelly-Phillips',
    author_email='martin@4degrees.ltd.uk',
    license='Apache License (2.0)',
    packages=[
        'lucidity',
    ],
    package_dir={
        '': 'source'
    },
    install_requires=[
        'regex >= 2.4.26',
        'bunch >= 1.0.1'
    ],
    tests_require=['pytest >= 2.3.5'],
    cmdclass={
        'test': PyTest
    },
    zip_safe=False
)

