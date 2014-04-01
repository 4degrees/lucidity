# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import copy

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


@pytest.mark.parametrize(('path', 'anchor', 'expected'), [
    ('/static/value/extra', Template.ANCHOR_START, True),
    ('/static/', Template.ANCHOR_START, False),
    ('/extra/static/value', Template.ANCHOR_END, True),
    ('/static/value/extra', Template.ANCHOR_END, False),
    ('/static/value', Template.ANCHOR_BOTH, True),
    ('extra/static/value', Template.ANCHOR_BOTH, False),
    ('/static/value/extra', Template.ANCHOR_BOTH, False),
    ('extra/static/value/extra', None, True),
    ('extra/non/matching/extra', None, False)
], ids=[
    'anchor_start:matching string',
    'anchor_start:non-matching string',
    'anchor_end:matching string',
    'anchor_end:non-matching string',
    'anchor_both:matching string',
    'anchor_both:non-matching string prefix',
    'anchor_both:non-matching string suffix',
    'anchor_none:matching string',
    'anchor_none:non-matching string'
])
def test_anchor(path, anchor, expected):
    '''Parse path with specific anchor setting.'''
    pattern = '/static/{variable}'
    template = Template('test', pattern, anchor=anchor)

    if not expected:
        with pytest.raises(ParseError):
            template.parse(path)
    else:
        data = template.parse(path)
        assert data == {'variable': 'value'}


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
    ('/{variable_a}/{variable_b}', {'variable_a': 'value'}),
    ('{nested.variable}', {}),
    ('{nested.variable}', {'nested': {}}),
], ids=[
    'missing single variable',
    'partial data',
    'missing top level nested variable',
    'missing nested variable'
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


def test_escaping_pattern():
    '''Escape regex components in pattern.'''
    template = Template('test', '{filename}.{index:\d\\{4\\}}.{ext}')
    expected = {'filename': 'filename', 'index': '0001', 'ext': 'ext'}
    assert template.parse('filename.0001.ext') == expected


@pytest.mark.parametrize(('pattern', 'expected'), [
    ('/static/string', []),
    ('/single/{variable}', ['variable']),
    ('/{variable}/{variable}', ['variable']),
    ('/static/{variable:\d\{4\}}', ['variable']),
    ('/{a}/static/{b}', ['a', 'b']),
    ('/{a.b.c}/static/{a.b.d}', ['a.b.c', 'a.b.d']),
    ('/{a}_{b}', ['a', 'b'])
], ids=[
    'static string',
    'single variable',
    'duplicate variable',
    'custom variable expression',
    'mix of static and variables',
    'structured placeholders',
    'neighbouring variables'
])
def test_keys(pattern, expected):
    '''Get keys in pattern.'''
    template = Template('test', pattern)
    placeholders = template.keys()
    assert sorted(placeholders) == sorted(expected)


def test_keys_mutable_side_effect():
    '''Avoid side effects mutating internal keys set.'''
    template = Template('test', '/single/{variable}')
    placeholders = template.keys()
    assert placeholders == set(['variable'])

    # Mutate returned set.
    placeholders.add('other')

    # Newly returned set should be unaffected.
    placeholders_b = template.keys()
    assert placeholders_b == set(['variable'])


def test_deepcopy():
    '''Deepcopy template.'''
    template = Template('test', '/single/{variable}')
    copied_template = copy.deepcopy(template)

    assert template._regex == copied_template._regex
