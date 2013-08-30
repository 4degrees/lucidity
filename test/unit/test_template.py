# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import pytest

from lucidity import Template


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


@pytest.mark.parametrize(('pattern', 'input', 'expected'), [
    ('/static/string', '/static/string', {}),
    ('/single/{variable}', '/single/value', {'variable': 'value'}),
    ('/{variable}/{variable}', '/first/second', {'variable': 'second'}),
    ('/static/{variable:\d\{4\}}', '/static/1234', {'variable': '1234'}),
    ('/{a}/static/{b}', '/first/static/second', {'a': 'first', 'b': 'second'}),
    ('/{a.b.c}/static/{a.b.d}', '/first/static/second',
     {'a': {'b': {'c': 'first', 'd': 'second'}}}),
], ids=[
    'static string',
    'single variable',
    'duplicate variable',
    'custom variable expression',
    'mix of static and variables',
    'structured placeholders'
])
def test_matching_parse(pattern, input, expected):
    '''Extract data from matching input.'''
    template = Template('test', pattern)
    data = template.parse(input)
    assert data == expected


@pytest.mark.parametrize(('pattern', 'input'), [
    ('/static/string', '/static/string/'),
    ('/static/string', '/static/'),
    ('/single/{variable}', '/static/'),
    ('/static/{variable:\d+}', '/static/foo')
], ids=[
    'string too long',
    'string too short',
    'missing variable',
    'mismatching custom expression'
])
def test_non_matching_parse(pattern, input):
    '''Extract data from non-matching input.'''
    template = Template('test', pattern)
    data = template.parse(input)
    assert data is None


@pytest.mark.parametrize(('pattern', 'input', 'expected'), [
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
def test_format(pattern, input, expected):
    '''Format input against pattern.'''
    template = Template('test', pattern)
    formatted = template.format(input)
    assert formatted == expected


def test_repr():
    '''Represent template.'''
    assert (repr(Template('test', '/foo/{bar}/{baz:\d+}'))
            == 'Template(name=\'test\', pattern=\'/foo/{bar}/{baz:\\\d+}\')')
