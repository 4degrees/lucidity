# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import sys
import re
import functools
import copy
from collections import defaultdict

import lucidity.error

# Type of a RegexObject for isinstance check.
_RegexType = type(re.compile(''))


class Template(object):
    '''A template.'''

    _STRIP_EXPRESSION_REGEX = re.compile(r'{(.+?)(:(\\}|.)+?)}')
    _PLAIN_PLACEHOLDER_REGEX = re.compile(r'{(.+?)}')

    ANCHOR_START, ANCHOR_END, ANCHOR_BOTH = (1, 2, 3)

    RELAXED, STRICT = (1, 2)

    def __init__(self, name, pattern, anchor=ANCHOR_START,
                 default_placeholder_expression='[\w_.\-]+',
                 duplicate_placeholder_mode=RELAXED):
        '''Initialise with *name* and *pattern*.

        *anchor* determines how the pattern is anchored during a parse. A
        value of :attr:`~Template.ANCHOR_START` (the default) will match the
        pattern against the start of a path. :attr:`~Template.ANCHOR_END` will
        match against the end of a path. To anchor at both the start and end
        (a full path match) use :attr:`~Template.ANCHOR_BOTH`. Finally,
        ``None`` will try to match the pattern once anywhere in the path.

        *duplicate_placeholder_mode* determines how duplicate placeholders will
        be handled during parsing. :attr:`~Template.RELAXED` mode extracts the
        last matching value without checking the other values.
        :attr:`~Template.STRICT` mode ensures that all duplicate placeholders
        extract the same value and raises :exc:`~lucidity.error.ParseError` if
        they do not.

        '''
        super(Template, self).__init__()
        self.duplicate_placeholder_mode = duplicate_placeholder_mode
        self._default_placeholder_expression = default_placeholder_expression
        self._period_code = '_LPD_'
        self._name = name
        self._pattern = pattern
        self._anchor = anchor
        self._regex = self._construct_regular_expression(self.pattern)
        self._format_specification = self._construct_format_specification(
            self.pattern
        )
        self._placeholders = self._extract_placeholders(
            self._format_specification
        )

    def __repr__(self):
        '''Return unambiguous representation of template.'''
        return '{0}(name={1!r}, pattern={2!r})'.format(
            self.__class__.__name__, self.name, self.pattern
        )

    def __deepcopy__(self, memo):
        '''Return deep copy of template.'''
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result

        for key, value in self.__dict__.items():
            if isinstance(value, _RegexType):
                # RegexObject is not deepcopyable, so store a new instance
                # compiled using the same pattern. Note that the compiled result
                #  will typically be the same instance.
                setattr(result, key, re.compile(value.pattern))
            else:
                setattr(result, key, copy.deepcopy(value, memo))

        return result

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
        parsable by this template.

        '''
        parsed = {}

        match = self._regex.search(path)
        if match:
            data = {}
            for key, value in sorted(match.groupdict().items()):
                # Strip number that was added to make group name unique.
                key = key[:-3]

                # If strict mode enabled for duplicate placeholders, ensure that
                # all duplicate placeholders extract the same value.
                if self.duplicate_placeholder_mode == self.STRICT:
                    if key in parsed:
                        if parsed[key] != value:
                            raise lucidity.error.ParseError(
                                'Different extracted values for placeholder '
                                '{0!r} detected. Values were {1!r} and {2!r}.'
                                .format(key, parsed[key], value)
                            )
                    else:
                        parsed[key] = value

                # Expand dot notation keys into nested dictionaries.
                target = data

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
        def _format(match):
            '''Return value from data for *match*.'''
            placeholder = match.group(1)
            parts = placeholder.split('.')

            try:
                value = data
                for part in parts:
                    value = value[part]

            except (TypeError, KeyError):
                raise lucidity.error.FormatError(
                    'Could not format data {0!r} due to missing key {1!r}.'
                    .format(data, placeholder)
                )

            else:
                return value

        return self._PLAIN_PLACEHOLDER_REGEX.sub(
            _format, self._format_specification
        )

    def keys(self):
        '''Return unique set of placeholders in pattern.'''
        return self._placeholders.copy()

    def _extract_placeholders(self, pattern):
        '''Extract and return unique set of placeholders in *pattern*.'''
        return set(self._PLAIN_PLACEHOLDER_REGEX.findall(pattern))

    def _construct_format_specification(self, pattern):
        '''Return format specification from *pattern*.'''
        return self._STRIP_EXPRESSION_REGEX.sub('{\g<1>}', pattern)

    def _construct_regular_expression(self, pattern):
        '''Return a regular expression to represent *pattern*.'''
        # Escape non-placeholder components.
        expression = re.sub(
            r'(?P<placeholder>{(.+?)(:(\\}|.)+?)?})|(?P<other>.+?)',
            self._escape,
            pattern
        )

        # Replace placeholders with regex pattern.
        expression = re.sub(
            r'{(?P<placeholder>.+?)(:(?P<expression>(\\}|.)+?))?}',
            functools.partial(
                self._convert, placeholder_count=defaultdict(int)
            ),
            expression
        )

        if self._anchor is not None:
            if bool(self._anchor & self.ANCHOR_START):
                expression = '^{0}'.format(expression)

            if bool(self._anchor & self.ANCHOR_END):
                expression = '{0}$'.format(expression)

        # Compile expression.
        try:
            compiled = re.compile(expression)
        except re.error as error:
            if any([
                'bad group name' in str(error),
                'bad character in group name' in str(error)
            ]):
                raise ValueError('Placeholder name contains invalid '
                                 'characters.')
            else:
                _, value, traceback = sys.exc_info()
                message = 'Invalid pattern: {0}'.format(value)
                raise ValueError, message, traceback  #@IgnorePep8

        return compiled

    def _convert(self, match, placeholder_count):
        '''Return a regular expression to represent *match*.

        *placeholder_count* should be a `defaultdict(int)` that will be used to
        store counts of unique placeholder names.

        '''
        placeholder_name = match.group('placeholder')

        # Support period (.) as nested key indicator. Currently, a period is
        # not a valid character for a group name in the standard Python regex
        # library. Rather than rewrite or monkey patch the library work around
        # the restriction with a unique identifier.
        placeholder_name = placeholder_name.replace('.', self._period_code)

        # The re module does not support duplicate group names. To support
        # duplicate placeholder names in templates add a unique count to the
        # regular expression group name and strip it later during parse.
        placeholder_count[placeholder_name] += 1
        placeholder_name += '{0:03d}'.format(
            placeholder_count[placeholder_name]
        )

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
            return re.escape(groups['other'])

        return groups['placeholder']


class Resolver(object):
    '''Template resolver interface.'''

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get(self, template_name, default=None):
        '''Return template that matches *template_name*.

        If no template matches then return *default*.

        '''
        return default

    @classmethod
    def __subclasshook__(cls, subclass):
        '''Return whether *subclass* fulfils this interface.'''
        if cls is Resolver:
            return callable(getattr(subclass, 'get', None))

        return NotImplemented
