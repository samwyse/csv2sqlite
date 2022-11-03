"""Argparser actions that let you use mapping objects as choices."""

# Insure maximum compatibility between Python 2 and 3
from __future__ import absolute_import, division, print_function

# Metadate...
__author__ = "Samuel T. Denton, III <sam.denton@dell.com>"
__contributors__ = []
__copyright__ = "Copyright 2021 Samuel T. Denton, III"
__version__ = '0.9'

# Declutter our namespace
__all__ = ['StoreMapping', 'AppendMapping', 'ExtendMapping']

# Python standard libraries
import argparse

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

if __name__ == '__main__':
    import doctest
    doctest.testmod()
