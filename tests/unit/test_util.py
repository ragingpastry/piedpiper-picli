from picli import util

import pytest


def test_camelize():
    assert "Foo" == util.camelize("foo")
    assert "FooBar" == util.camelize("foo_bar")
    assert "FooBarBaz" == util.camelize("foo_bar_baz")


def test_merge_dicts():
    # example taken from python-anyconfig/anyconfig/__init__.py
    a = {"b": [{"c": 0}, {"c": 2}], "d": {"e": "aaa", "f": 3}}
    b = {"a": 1, "b": [{"c": 3}], "d": {"e": "bbb"}}
    x = {"a": 1, "b": [{"c": 3}], "d": {"e": "bbb", "f": 3}}

    assert x == util.merge_dicts(a, b)


def test_safe_load():
    assert {"foo": "bar"} == util.safe_load("foo: bar")


def test_safe_load_returns_empty_dict_on_empty_string():
    assert {} == util.safe_load("")


def test_safe_load_exits_when_cannot_parse():
    data = """
---
%foo:
""".strip()

    with pytest.raises(SystemExit) as e:
        util.safe_load(data)

    assert 1 == e.value.code
