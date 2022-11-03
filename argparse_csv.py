#! /usr/bin/env python

"""How to use this...

# Use "exit_on_error=False" to make doctest happier.
>>> parser = argparse.ArgumentParser(exit_on_error=False)

>>> csv_group = parser.add_csv_group(
...     title="CSV format",
...     description="Specify the details of the CSV file format.")

>>> ns = parser.parse_args('--delimiter / --quoting none'.split())
>>> argparser_dialect = csv_group.get_dialect(ns)
>>> csvout = csv.writer(sys.stdout, dialect=argparser_dialect)

>>> ns = parser.parse_args('--delimiter / --quoting all'.split())
>>> argparser_dialect = csv_group.get_dialect(ns)
>>> csvout = csv.writer(sys.stdout, dialect=argparser_dialect)
Traceback (most recent call last):
    ...
TypeError: quotechar must be set if quoting enabled

>>> ns = parser.parse_args('--delimiter / --quoting all --quotechar ='.split())
>>> argparser_dialect = csv_group.get_dialect(ns)
>>> csvout = csv.writer(sys.stdout, dialect=argparser_dialect)

"""

# Insure maximum compatibility between Python 2 and 3
from __future__ import absolute_import, division, print_function

# Metadate...
__author__ = "Samuel T. Denton, III <sam.denton@dell.com>"
__contributors__ = []
__copyright__ = "Copyright 2021 Samuel T. Denton, III"
__version__ = '0.9'

# Declutter our namespace
__all__ = []

# Python standard libraries
import argparse, csv, sys

# https://bugs.python.org/issue34188#msg323681
class StoreMapping(argparse._StoreAction):
    """
    Argparse action that interprets the `choices` argument as a dict
    mapping the user-specified choices values to the resulting option
    values.
    
    >>> adict = {'rock': 4, 'paper': 5, 'scissors': 8}
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument('--foo', action=StoreMapping, choices=adict)  # doctest: +ELLIPSIS
    StoreMapping(option_strings=['--foo'], dest='foo', ...)
    >>> parser.parse_args('--foo rock'.split())
    Namespace(foo=4)
    """
    def __init__(self, *args, choices, **kwargs):
        super().__init__(*args, choices=choices.keys(), **kwargs)
        self.mapping = choices
    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest, self.mapping[value])

class AppendMapping(StoreMapping):
    """
    >>> adict = {'rock': 4, 'paper': 5, 'scissors': 8}
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument('--foo', action=AppendMapping, choices=adict)  # doctest: +ELLIPSIS
    AppendMapping(option_strings=['--foo'], dest='foo', ...)
    >>> parser.parse_args('--foo rock --foo scissors'.split())
    Namespace(foo=[4, 8])
    """
    def __call__(self, parser, namespace, value, option_string=None):
        items = getattr(namespace, self.dest, None)
        items = argparse._copy_items(items)
        items.append(self.mapping[value])
        setattr(namespace, self.dest, items)

class ExtendMapping(StoreMapping):
    """
    >>> adict = {'rock': 4, 'paper': 5, 'scissors': 8}
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument('--foo', action=ExtendMapping, choices=adict, nargs='+')  # doctest: +ELLIPSIS
    ExtendMapping(option_strings=['--foo'], dest='foo', nargs='+', ...)
    >>> parser.parse_args(["--foo", "rock", "--foo", "paper", "scissors", "rock"])
    Namespace(foo=[4, 5, 8, 4])
    """
    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, None)
        items = argparse._copy_items(items)
        items.extend(self.mapping[value] for value in values)
        setattr(namespace, self.dest, items)

def singlechar(s):
    """Validate that 's' is a single character."""
    try:
        if len(s) == 1:
            return s
    except:
        pass
    raise ValueError('must be a single character')

quoting_choices = {
    name[6:].lower(): getattr(csv, name)
    for name in dir(csv) if name.startswith('QUOTE_')
    }

try:
    is_bool = {'action': argparse.BooleanOptionalAction}
except AttributeError:
    is_bool = {'action': 'store_true'}

is_char = {'type': singlechar, 'metavar': 'CHAR'}

dialect_attributes = (
    ('delimiter', is_char),
    ('quotechar', is_char),
    ('escapechar', is_char),
    ('doublequote', is_bool),
    ('skipinitialspace', is_bool),
    ('lineterminator', {'metavar': 'STR'}),
    ('quoting', {'action': StoreMapping, 'choices': quoting_choices}),
    )

def add_csv_group(container, *args, **kwargs):
    """Add an argument group to the given parser, using the given title
    and description.  The returned group has a property 'get_dialect'
    that's a function to create a CSV Dialect object from a Namespace
    object built from parsing a command line."""

    group = container.add_argument_group(
        title=kwargs.get('title'),
        description=kwargs.get('description'))

    prefix = kwargs.get('prefix')
    if prefix:
        arg_prefix = '--' + prefix + '-'
        attr_prefix = prefix + '_'
    else:
        arg_prefix = '--'
        attr_prefix = ''

    for name, kwds in dialect_attributes:
        group.add_argument(arg_prefix+name, **kwds)

    def get_dialect(ns):
        """Build a CSV Dialect from an argparse Namespace"""
        class dialect(csv.Dialect):
            _name = "argparser_dialect"
            lineterminator = '\r\n'
            quoting = csv.QUOTE_NONE
        for key, _ in dialect_attributes:
            attr_name = attr_prefix + key
            attr_value = getattr(ns, attr_name)
            if attr_value is not None:
                setattr(dialect, key, attr_value)
        return dialect

    group.get_dialect = get_dialect
    return group

# monkey-patch argparse to make 'add_csv_group' look native
argparse._ActionsContainer.add_csv_group = add_csv_group
del add_csv_group

if __name__ == '__main__':
    import doctest
    doctest.testmod()


