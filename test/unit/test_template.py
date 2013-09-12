# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import pytest

from lucidity import Template
from lucidity.error import ParseError, FormatError


@pytest.mark.parametrize('pattern', [
    '',
    '{variable}',
    '{dotted.variable}',
    '{variable}/{variable}',
    '{variable:\w+?}'
], ids=[
    'empty',
    'single variable',
    'dotted variable',
    'duplicate variable',
    'custom expression'
])
def test_valid_pattern(pattern):
    '''Construct template with valid pattern.'''
    Template('test', pattern)


@pytest.mark.parametrize('pattern', [
    '{}',
    '{variable-dashed}',
    '{variable:(?P<missing_closing_angle_bracket)}'
], ids=[
    'empty placeholder',
    'invalid placeholder character', 'as'
])
def test_invalid_pattern(pattern):
    '''Construct template with invalid pattern.'''
    with pytest.raises(ValueError):
        Template('test', pattern)


@pytest.mark.parametrize(('pattern', 'path', 'expected'), [
    ('/static/string', '/static/string', {}),
    ('/single/{variable}', '/single/value', {'variable': 'value'}),
    ('/{variable}/{variable}', '/first/second', {'variable': 'second'}),
    ('/static/{variable:\d\{4\}}', '/static/1234', {'variable': '1234'}),
    ('/{a}/static/{b}', '/first/static/second', {'a': 'first', 'b': 'second'}),
    ('/{a.b.c}/static/{a.b.d}', '/first/static/second',
     {'a': {'b': {'c': 'first', 'd': 'second'}}}),
    ('/{a}_{b}', '/first_second', {'a': 'first', 'b': 'second'})
], ids=[
    'static string',
    'single variable',
    'duplicate variable',
    'custom variable expression',
    'mix of static and variables',
    'structured placeholders',
    'neighbouring variables'
])
def test_matching_parse(pattern, path, expected):
    '''Extract data from matching path.'''
    template = Template('test', pattern)
    data = template.parse(path)
    assert data == expected


@pytest.mark.parametrize(('pattern', 'path'), [
    ('/static/string', '/static/'),
    ('/single/{variable}', '/static/'),
    ('/static/{variable:\d+}', '/static/foo')
], ids=[
    'string too short',
    'missing variable',
    'mismatching custom expression'
])
def test_non_matching_parse(pattern, path):
    '''Extract data from non-matching path.'''
    template = Template('test', pattern)
    with pytest.raises(ParseError):
        data = template.parse(path)


@pytest.mark.parametrize(('pattern', 'data', 'expected'), [
    ('/static/string', {}, '/static/string'),
    ('/single/{variable}', {'variable': 'value'}, '/single/value'),
    ('/{variable}/{variable}', {'variable': 'value'}, '/value/value'),
    ('/static/{variable:\d\{4\}}', {'variable': '1234'}, '/static/1234'),
    ('/{a}/static/{b}', {'a': 'first', 'b': 'second'}, '/first/static/second'),
    ('/{a.b.c}/static/{a.b.d}', {'a': {'b': {'c': 'first', 'd': 'second'}}},
     '/first/static/second'),
], ids=[
    'static string',
    'single variable',
    'duplicate variable',
    'custom variable expression',
    'mix of static and variables',
    'structured placeholders'
])
def test_format(pattern, data, expected):
    '''Format data against pattern.'''
    template = Template('test', pattern)
    formatted = template.format(data)
    assert formatted == expected


@pytest.mark.parametrize(('pattern', 'data'), [
    ('/single/{variable}', {}),
    ('/{variable_a}/{variable_b}', {'variable_a': 'value'})
], ids=[
    'missing single variable',
    'partial data'
])
def test_format_failure(pattern, data):
    '''Format incomplete data against pattern.'''
    template = Template('test', pattern)
    with pytest.raises(FormatError):
        template.format(data)


def test_repr():
    '''Represent template.'''
    assert (repr(Template('test', '/foo/{bar}/{baz:\d+}'))
            == 'Template(name=\'test\', pattern=\'/foo/{bar}/{baz:\\\d+}\')')
