# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import sys

import regex as _regex
import bunch

import lucidity.error


class Template(object):
    '''A template.'''

    _STRIP_EXPRESSION_REGEX = _regex.compile(r'{(.+?)(:(\\}|.)+?)}')

    ANCHOR_START, ANCHOR_END, ANCHOR_BOTH = (1, 2, 3)

    def __init__(self, name, pattern, anchor=ANCHOR_START,
                 default_placeholder_expression='[\w_.\-]+'):
        '''Initialise with *name* and *pattern*.

        *anchor* determines how the pattern is anchored during a parse. A
        value of :attr:`~Template.ANCHOR_START` (the default) will match the
        pattern against the start of a path. :attr:`~Template.ANCHOR_END` will
        match against the end of a path. To anchor at both the start and end
        (a full path match) use :attr:`~Template.ANCHOR_BOTH`. Finally,
        ``None`` will try to match the pattern once anywhere in the path.

        '''
        super(Template, self).__init__()
        self._default_placeholder_expression = default_placeholder_expression
        self._period_code = '_LPD_'
        self._name = name
        self._pattern = pattern
        self._anchor = anchor
        self._regex = self._construct_regular_expression(self.pattern)
        self._format = self._construct_format_expression(self.pattern)
        self._placeholders = self._extract_placeholders(self.pattern)

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

    def parse(self, path):
        '''Return dictionary of data extracted from *path* using this template.

        Raise :py:class:`~lucidity.error.ParseError` if *path* is not
        parseable by this template.

        '''
        match = self._regex.search(path)
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
                'Path {0!r} did not match template pattern.'.format(path)
            )

    def format(self, data):
        '''Return a path formatted by applying *data* to this template.

        Raise :py:class:`~lucidity.error.FormatError` if *data* does not
        supply enough information to fill the template fields.

        '''
        bunchified = bunch.bunchify(data)
        try:
            path = self._format.format(**bunchified)
        except (AttributeError, KeyError) as error:
            raise lucidity.error.FormatError(
                'Could not format data {0!r} due to missing key {1!r}.'
                .format(data, error.args[0])
            )
        else:
            return path

    def keys(self):
        return self._placeholders

    def _extract_placeholders(self, pattern):
        match = _regex.findall(r'(?P<placeholder>{(.+?)(:(\\}|.)+?)?})', pattern)
        return list(set([g[1] for g in match]))

    def _construct_format_expression(self, pattern):
        '''Return format expression from *pattern*.'''
        return self._STRIP_EXPRESSION_REGEX.sub('{\g<1>}', pattern)

    def _construct_regular_expression(self, pattern):
        '''Return a regular expression to represent *pattern*.'''
        # Escape non-placeholder components.
        expression = _regex.sub(
            r'(?P<placeholder>{(.+?)(:(\\}|.)+?)?})|(?P<other>.+?)',
            self._escape,
            pattern
        )

        # Replace placeholders with regex pattern.
        expression = _regex.sub(
            r'{(?P<placeholder>.+?)(:(?P<expression>(\\}|.)+?))?}',
            self._convert,
            expression
        )

        if self._anchor is not None:
            if bool(self._anchor & self.ANCHOR_START):
                expression = '^{0}'.format(expression)

            if bool(self._anchor & self.ANCHOR_END):
                expression = '{0}$'.format(expression)

        # Compile expression.
        try:
            compiled = _regex.compile(expression)
        except _regex._regex_core.error as error:
            if 'bad group name' in error:
                raise ValueError('Placeholder name contains invalid '
                                 'characters.')
            else:
                _, value, traceback = sys.exc_info()
                message = 'Invalid pattern: {0}'.format(value)
                raise ValueError, message, traceback  #@IgnorePep8

        return compiled

    def _convert(self, match):
        '''Return a regular expression to represent *match*.'''
        placeholder_name = match.group('placeholder')

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

    def _escape(self, match):
        '''Escape matched 'other' group value.'''
        groups = match.groupdict()
        if groups['other'] is not None:
            return _regex.escape(groups['other'])

        return groups['placeholder']

