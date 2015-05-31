# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import pytest

from lucidity import Template, Resolver
from lucidity.error import ParseError, FormatError, ResolveError


class ResolverFixture(Resolver):
    '''Example resolver.'''

    def __init__(self, templates=None):
        '''Initialise resolver with templates.'''
        super(ResolverFixture, self).__init__()
        self.templates = templates or []

    def get(self, template_name, default=None):
        '''Return template with *template_name*.

        If no template matches then return *default*.

        '''
        for template in self.templates:
            if template.name == template_name:
                return template

        return default


@pytest.fixture(scope='session')
def template_resolver():
    '''Return template resolver instance.'''
    resolver = ResolverFixture()
    resolver.templates.extend([
        Template('reference', '{variable}', template_resolver=resolver),
        Template('nested', '/root/{@reference}', template_resolver=resolver)
    ])
    return resolver


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
    'invalid placeholder character',
    'invalid placeholder expression'
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
    ('/{a}_{b}', '/first_second', {'a': 'first', 'b': 'second'}),
    ('/single/{@reference}', '/single/value', {'variable': 'value'}),
    ('{@nested}/reference', '/root/value/reference', {'variable': 'value'})
], ids=[
    'static string',
    'single variable',
    'duplicate variable',
    'custom variable expression',
    'mix of static and variables',
    'structured placeholders',
    'neighbouring variables',
    'single reference',
    'nested reference'
])
def test_matching_parse(pattern, path, expected, template_resolver):
    '''Extract data from matching path.'''
    template = Template('test', pattern, template_resolver=template_resolver)
    data = template.parse(path)
    assert data == expected


@pytest.mark.parametrize(('pattern', 'path'), [
    ('/static/string', '/static/'),
    ('/single/{variable}', '/static/'),
    ('/static/{variable:\d+}', '/static/foo'),
    ('/single/{variable}/{@reference}', '/single/value/'),
    ('{@nested}/reference', '/root/value')
], ids=[
    'string too short',
    'missing variable',
    'mismatching custom expression',
    'string not accounting for reference',
    'string not accounting for nested reference'
])
def test_non_matching_parse(pattern, path, template_resolver):
    '''Extract data from non-matching path.'''
    template = Template('test', pattern, template_resolver=template_resolver)
    with pytest.raises(ParseError):
        data = template.parse(path)


@pytest.mark.parametrize(('pattern', 'path', 'expected'), [
    ('/{variable}/{variable}', '/value/value', {'variable': 'value'}),
    ('/static/{variable:\d\{4\}}/other/{variable}', '/static/1234/other/1234',
     {'variable': '1234'}),
    ('/{a.b.c}/static/{a.b.c}', '/value/static/value',
     {'a': {'b': {'c': 'value'}}}),
    ('/{a}/{b}/other/{a}_{b}', '/a/b/other/a_b', {'a': 'a', 'b': 'b'}),
    ('{@nested}/{variable}', '/root/value/value', {'variable': 'value'})
], ids=[
    'simple duplicate',
    'duplicate with one specialised expression',
    'structured duplicate',
    'multiple duplicates',
    'duplicate from reference'
])
def test_valid_parse_in_strict_mode(pattern, path, expected, template_resolver):
    '''Extract data in strict mode when no invalid duplicates detected.'''
    template = Template(
        'test', pattern, duplicate_placeholder_mode=Template.STRICT,
        template_resolver=template_resolver
    )
    data = template.parse(path)
    assert data == expected


@pytest.mark.parametrize(('pattern', 'path'), [
    ('/{variable}/{variable}', '/a/b'),
    ('/static/{variable:\d\{4\}}/other/{variable}', '/static/1234/other/2345'),
    ('/{a.b.c}/static/{a.b.c}', '/c1/static/c2'),
    ('/{a}/{b}/other/{a}_{b}', '/a/b/other/c_d'),
    ('{@nested}/{variable}', '/root/different/value')
], ids=[
    'simple duplicate',
    'duplicate with one specialised expression',
    'structured duplicate',
    'multiple duplicates',
    'duplicate from reference'
])
def test_invalid_parse_in_strict_mode(pattern, path, template_resolver):
    '''Fail to extract data in strict mode when invalid duplicates detected.'''
    template = Template(
        'test', pattern, duplicate_placeholder_mode=Template.STRICT,
        template_resolver=template_resolver
    )
    with pytest.raises(ParseError) as exception:
        template.parse(path)

    assert 'Different extracted values' in str(exception.value)


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
    ('/single/{@reference}', {'variable': 'value'}, '/single/value'),
    ('{@nested}/reference', {'variable': 'value'}, '/root/value/reference'),
], ids=[
    'static string',
    'single variable',
    'duplicate variable',
    'custom variable expression',
    'mix of static and variables',
    'structured placeholders',
    'reference',
    'nested reference'
])
def test_format(pattern, data, expected, template_resolver):
    '''Format data against pattern.'''
    template = Template('test', pattern, template_resolver=template_resolver)
    formatted = template.format(data)
    assert formatted == expected


@pytest.mark.parametrize(('pattern', 'data'), [
    ('/single/{variable}', {}),
    ('/{variable_a}/{variable_b}', {'variable_a': 'value'}),
    ('{nested.variable}', {}),
    ('{nested.variable}', {'nested': {}}),
    ('/single/{@reference}', {'some': 'value'}),
    ('{@nested}/reference', {'some': 'value'}),

], ids=[
    'missing single variable',
    'partial data',
    'missing top level nested variable',
    'missing nested variable',
    'reference',
    'nested reference'
])
def test_format_failure(pattern, data, template_resolver):
    '''Format incomplete data against pattern.'''
    template = Template('test', pattern, template_resolver=template_resolver)
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
    ('/{a}_{b}', ['a', 'b']),
    ('/{a}_{b}/{@reference}', ['a', 'b', 'variable']),
    ('/{a}_{b}/{@reference}/{variable}', ['a', 'b', 'variable'])
], ids=[
    'static string',
    'single variable',
    'duplicate variable',
    'custom variable expression',
    'mix of static and variables',
    'structured placeholders',
    'neighbouring variables',
    'single reference',
    'duplicate variable via reference'
])
def test_keys(pattern, expected, template_resolver):
    '''Get keys in pattern.'''
    template = Template('test', pattern, template_resolver=template_resolver)
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


@pytest.mark.parametrize(('instance', 'expected'), [
    (ResolverFixture(), True),
    ({}, True),
    ([], False),
], ids=[
    'subclass',
    'compliant non-subclass',
    'non-compliant non-subclass',
])
def test_resolver_interface_check(instance, expected):
    '''Correctly identify compliant Resolver implementations.'''
    assert isinstance(instance, Resolver) is expected


@pytest.mark.parametrize(('operation', 'arguments'), [
    ('parse', ('',)),
    ('format', ({},)),
    ('keys', ())
])
def test_missing_resolver(operation, arguments):
    '''Fail operations when missing resolver and using template references.'''
    template = Template('test', '{@reference}')
    with pytest.raises(ResolveError):
        getattr(template, operation)(*arguments)


@pytest.mark.parametrize(('operation', 'arguments'), [
    ('parse', ('',)),
    ('format', ({},)),
    ('keys', ())
])
def test_resolver_failure(operation, arguments):
    '''Fail operations when resolver unable to resolver template references.'''
    template = Template('test', '{@reference}', template_resolver={})
    with pytest.raises(ResolveError):
        getattr(template, operation)(*arguments)
