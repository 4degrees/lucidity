# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os
import operator

import pytest

import lucidity


TEST_TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'fixture', 'template'
) 


@pytest.fixture
def templates():
    '''Return candidate templates.'''
    return [
        lucidity.Template('model', '/jobs/{job.code}/assets/model/{lod}'),
        lucidity.Template('rig', '/jobs/{job.code}/assets/rig/{rig_type}')
    ]


@pytest.mark.parametrize(('recursive', 'expected'), [
    (True, ['a', 'b', 'c', 'd']),
    (False, ['a', 'b'])
], ids=[
    'recursive',
    'non-recursive'
])
def test_discover(recursive, expected):
    '''Discover templates via registration mount points.'''
    templates = lucidity.discover_templates(
        [TEST_TEMPLATE_PATH], recursive=recursive
    )
    assert map(operator.attrgetter('name'), templates) == expected


@pytest.mark.parametrize(('path', 'expected'), [
    (TEST_TEMPLATE_PATH, ['a', 'b', 'c', 'd']),
    (os.path.join(TEST_TEMPLATE_PATH, 'non-existant'), [])
], ids=[
    'valid path',
    'missing path'
])
def test_discover_with_env(path, expected, monkeypatch):
    '''Discover templates using environment variable.'''
    monkeypatch.setenv('LUCIDITY_TEMPLATE_PATH', path)
    templates = lucidity.discover_templates()
    assert map(operator.attrgetter('name'), templates) == expected


@pytest.mark.parametrize(('path', 'expected'), [
    ('/jobs/monty/assets/model/high',
     {'job': {'code': 'monty'}, 'lod': 'high'}),
    ('/jobs/monty/assets/rig/anim',
     {'job': {'code': 'monty'}, 'rig_type': 'anim'})
], ids=[
    'model',
    'rig'
])
def test_successfull_parse(path, expected, templates):
    '''Parse path successfully against multiple candidate templates.'''
    data, template = lucidity.parse(path, templates)
    assert data == expected


def test_unsuccessfull_parse(templates):
    '''Unsuccessful parse of path against multiple candidate templates.'''
    with pytest.raises(lucidity.ParseError):
        lucidity.parse('/not/matching', templates)


@pytest.mark.parametrize(('data', 'expected'), [
    ({'job': {'code': 'monty'}, 'lod': 'high'},
     '/jobs/monty/assets/model/high'),
    ({'job': {'code': 'monty'}, 'rig_type': 'anim'},
     '/jobs/monty/assets/rig/anim')
], ids=[
    'model',
    'rig'
])
def test_successfull_format(data, expected, templates):
    '''Format data successfully against multiple candidate templates.'''
    path, template = lucidity.format(data, templates)
    assert path == expected


@pytest.mark.parametrize('data', [
    {},
    {'lod': 'high'},
    {'job': {}, 'lod': 'high'},
    {'job': 'monty'},
], ids=[
    'empty data',
    'partial data',
    'missing nested variable',
    'invalid nested reference'
])
def test_unsuccessfull_format(data, templates):
    '''Unsuccessful formatting of data against multiple candidate templates.'''
    with pytest.raises(lucidity.FormatError):
        lucidity.format(data, templates)


