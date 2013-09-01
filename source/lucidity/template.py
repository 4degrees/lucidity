# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import sys

import regex as _regex
import bunch

import lucidity.error


class Template(object):
    '''A template.'''

    _STRIP_EXPRESSION_REGEX = _regex.compile(r'{(.*?)(:(\\}|.)+?)}')

    def __init__(self, name, pattern,
                 default_placeholder_expression='[\w_.\-]+?'):
        '''Initialise with *name* and *pattern*.'''
        super(Template, self).__init__()
        self._default_placeholder_expression = default_placeholder_expression
        self._period_code = '_LPD_'
        self._name = name
        self._pattern = pattern
        self._regex = self._construct_regular_expression(self.pattern)
        self._format = self._construct_format_expression(self.pattern)

    def __repr__(self):
        '''Return unambiguous representation of template.'''
        return '{0}(name={1!r}, pattern={2!r})'.format(
            self.__class__.__name__, self.name, self.pattern
        )

    @property
    def name(self):
        '''Return name of template.'''
        return self._name

    @property
    def pattern(self):
        '''Return template pattern.'''
        return self._pattern

    def parse(self, input):
        '''Return dictionary of data extracted from *input* using this template.

        Raise :py:class:`~lucidity.error.ParseError` if *input* is not
        parseable by this template.

        '''
        match = self._regex.fullmatch(input)
        if match:
            data = {}
            for key, value in match.groupdict().items():
                target = data

                # Expand dot notation keys into nested dictionaries.
                parts = key.split(self._period_code)
                for part in parts[:-1]:
                    target = target.setdefault(part, {})

                target[parts[-1]] = value

            return data

        else:
            raise lucidity.error.ParseError(
                'Input {0!r} did not match template pattern.'.format(input)
            )

    def format(self, data):
        '''Return a path formatted by applying *data* to this template.

        Raise :py:class:`~lucidity.error.FormatError` if *data* does not
        supply enough information to fill the template fields.

        '''
        bunchified = bunch.bunchify(data)
        try:
            path = self._format.format(**bunchified)
        except KeyError as error:
            raise lucidity.error.FormatError(
                'Could not format data {0!r} due to missing key {1!r}.'
                .format(data, error.args[0])
            )
        else:
            return path

    def _construct_format_expression(self, pattern):
        '''Return format expression from *pattern*.'''
        return self._STRIP_EXPRESSION_REGEX.sub('{\g<1>}', pattern)

    def _construct_regular_expression(self, pattern):
        '''Return a regular expression to represent *pattern*.'''
        expression = _regex.sub(
            r'{(?P<placeholder>.*?)(:(?P<expression>(\\}|.)+?))?}',
            self._convert,
            pattern
        )
        try:
            compiled = _regex.compile(expression)
        except _regex._regex_core.error as error:
            if 'bad group name' in error:
                raise ValueError('Placeholder name contains invalid '
                                 'characters.')
            else:
                type, value, traceback = sys.exc_info()
                message = 'Invalid pattern: {0}'.format(value)
                raise ValueError, message, traceback

        return compiled

    def _convert(self, match):
        '''Return a regular expression to represent *match*.'''
        placeholder_name = match.group('placeholder')
        if not placeholder_name:
            raise ValueError('Placeholder name not specified.')

        # Support period (.) as nested key indicator. Currently, a period is
        # not a valid character for a group name in the standard Python regex
        # library. Rather than rewrite or monkey patch the library work around
        # the restriction with a unique identifier.
        placeholder_name = placeholder_name.replace('.', self._period_code)

        expression = match.group('expression')
        if expression is None:
            expression = self._default_placeholder_expression

        # Un-escape potentially escaped characters in expression.
        expression = expression.replace('\{', '{').replace('\}', '}')

        return r'(?P<{0}>{1})'.format(placeholder_name, expression)

