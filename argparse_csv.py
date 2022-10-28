#! /usr/bin/env python

"""Command line arguments to define CSV dialects."""

# Insure maximum compatibility between Python 2 and 3
from __future__ import absolute_import, division, print_function

try:
    basestring
except NameError:
    basestring = str

# Metadate...
__author__ = "Samuel T. Denton, III <sam.denton@dell.com>"
__contributors__ = []
__copyright__ = "Copyright 2021 Samuel T. Denton, III"
__version__ = '0.9'

# Declutter our namespace
__all__ = ['add_csv_argments']

# Python standard libraries
import argparse, csv

def singlechar(s):
    """Argument must be a single character."""
    try:
        if len(s) == 1:
            return s
    except:
        pass
    raise ValueError('must be a single character')

# Allowed ways of quoting
quoting_choices = {
    name[6:].lower(): getattr(csv, name)
    for name in dir(csv) if name.startswith('QUOTE_')}

# The various types of values in a Dialect
is_bool = {'action': 'store_true'}
is_char = {'type': singlechar, 'metavar': 'CHAR'}
is_string = {'type': str, 'metavar': 'STR'}
is_quoting = {'choices': quoting_choices, 'type': quoting_choices.get}

dialect_attributes = (
    ('delimiter', is_char),
    ('quotechar', is_char),
    ('escapechar', is_char),
    ('doublequote', is_bool),
    ('skipinitialspace', is_bool),
    ('lineterminator', is_string),
    ('quoting', is_quoting),
    )

def add_csv_argments(parser, title=None, description=None, prefix='csv'):
    """Add an argument group to the given parser, using the given title
    and description.  Return a function to create a CSV Dialect object from
the Namespace object built from parsing a command line:

>>> parser = argparse.ArgumentParser()

>>> dialect_builder = add_csv_argments(parser, title="CSV format",
...     description="Specify the details of the CSV file format.")

>>> ns = parser.parse_args([])
>>> dialect = dialect_builder(ns)

>>> dialect.lineterminator
'\\r\\n'
>>> dialect.skipinitialspace
False
>>> dialect.quoting == csv.QUOTE_MINIMAL
True
>>> dialect.delimiter
','
>>> dialect.doublequote
False

"""

    new_group = parser.add_argument_group(title=title, description=description)
    if prefix:
        arg_prefix = '--' + prefix + '-'
        attr_prefix = prefix + '_'
    else:
        arg_prefix = '--'
        attr_prefix = ''
        
    for name, kwargs in dialect_attributes:
        new_group.add_argument(arg_prefix+name, **kwargs)

    def builder(args):
        """Build a CSV Dialect from an argparse Namespace"""
        class dialect(csv.excel):
            pass

        for key, _ in dialect_attributes:
            attr_name = attr_prefix + key
            attr_value = getattr(args, attr_name)
            if attr_value is not None:
                setattr(dialect, key, attr_value)
        return dialect
    return builder

if __name__ == '__main__':
    import doctest
    doctest.testmod()
