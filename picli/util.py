import anyconfig
from typing import Dict
import re


def merge_dicts(a: Dict, b: Dict) -> Dict:
    """
    Merges the values of B into A and returns a mutated dict A.
    ::
        dict a
        b:
           - c: 0
           - c: 2
        d:
           e: "aaa"
           f: 3
        dict b
        a: 1
        b:
           - c: 3
        d:
           e: "bbb"
    Will give an object such as::
        {'a': 1, 'b': [{'c': 3}], 'd': {'e': "bbb", 'f': 3}}
    :param a: the target dictionary
    :param b: the dictionary to import
    :return: dict
    """
    anyconfig.merge(a, b, ac_merge=anyconfig.MS_DICTS)

    return a

def render_runvars():
    pass

def camelize(string):
    return re.sub(r"(?:^|_)(.)", lambda m: m.group(1).upper(), string)

def memoize(function):
    memo = {}

    def wrapper(*args, **kwargs):
        if args not in memo:
            rv = function(*args, **kwargs)
            memo[args] = rv

            return rv
        return memo[args]

    return wrapper
