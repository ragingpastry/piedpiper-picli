import anyconfig
from typing import Dict
import re
import sys
import yaml
import uuid

from picli.logger import get_logger

LOG = get_logger(__name__)


class SafeDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(SafeDumper, self).increase_indent(flow, False)


def camelize(string):
    return re.sub(r"(?:^|_)(.)", lambda m: m.group(1).upper(), string)


def generate_run_id():
    return str(uuid.uuid4())


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


def safe_dump(data):
    return yaml.dump(
        data, Dumper=SafeDumper, default_flow_style=False, explicit_start=True
    )


def safe_load(string):
    try:
        return yaml.safe_load(string) or {}
    except yaml.scanner.ScannerError as e:
        sysexit_with_message(e)


def safe_load_file(filename):
    with open(filename) as file:
        return safe_load(file)


def sysexit_with_message(msg, code=1):
    LOG.critical(msg)
    sys.exit(code)
