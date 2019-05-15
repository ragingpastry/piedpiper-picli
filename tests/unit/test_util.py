import pytest
import requests
import responses
import urllib3
import uuid
import tempfile
import mock
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)

from picli import util


def test_merge_dicts():
    # example taken from python-anyconfig/anyconfig/__init__.py
    a = {'b': [{'c': 0}, {'c': 2}], 'd': {'e': 'aaa', 'f': 3}}
    b = {'a': 1, 'b': [{'c': 3}], 'd': {'e': 'bbb'}}
    x = {'a': 1, 'b': [{'c': 3}], 'd': {'e': "bbb", 'f': 3}}

    assert x == util.merge_dicts(a, b)

def test_generate_hashsum():
    test_file_1 = tempfile.NamedTemporaryFile()
    test_file_2 = tempfile.NamedTemporaryFile()
    for test_file in [test_file_1, test_file_2]:
        with open(test_file.name, 'w') as f:
            f.write('test')

    test_file_1_hash = util.generate_hashsum(test_file_1.name)
    test_file_2_hash = util.generate_hashsum(test_file_2.name)

    assert test_file_1_hash == test_file_2_hash


@mock.patch('picli.util.Minio', autospec=True)
def test_upload_artifact(mock_minio):
    minio_client_mock = mock.MagicMock()
    minio_client_mock.make_bucket.return_value = True
    minio_client_mock.fput_object.return_value = None
    minio_client_mock.fstat_object.return_value = None
    mock_minio.side_effect = minio_client_mock
    artifact = util.upload_artifact('test-bucket',
                                    'test-object',
                                    'test_file_path',
                                    '127.0.0.1',
                                    'test_access_key',
                                    'test_secret_key')
    minio_client_mock.return_value.fput_object.assert_called_with('test-bucket', 'test-object', 'test_file_path')

#@mock.patch('picli.util.Minio', autospec=True)
#def test_upload_artifact_response_error(mock_minio):
#    def side_effect_function():
#        class ResponseError(Exception):
#            pass
#        return ResponseError()
#
#    minio_client_mock = mock.MagicMock()
#    minio_client_mock.make_bucket.return_value = None
#    minio_client_mock.fput_object.side_effect = side_effect_function()
#    minio_client_mock.fstat_object.return_value = None
#    mock_minio.side_effect = minio_client_mock
#    artifact = util.upload_artifact('test-bucket',
#                                    'test-object',
#                                    'test_file_path',
#                                    '127.0.0.1',
#                                    'test_access_key',
#                                    'test_secret_key')
#
#    with mock.patch('picli.util.sysexit_with_message') as mock_exit:
#            mock_exit.assert_called_once()


def test_camelize():
    string_to_camel = 'camel_case'
    expected = 'CamelCase'
    camel_string = util.camelize(string_to_camel)

    assert expected == camel_string


def test_safe_dump():
    x = """
---
foo: bar
""".lstrip()

    assert x == util.safe_dump({'foo': 'bar'})


def test_safe_dump_with_increase_indent():
    data = {
        'foo': [{
            'foo': 'bar',
            'baz': 'zzyzx',
        }],
    }

    x = """
---
foo:
  - baz: zzyzx
    foo: bar
""".lstrip()
    assert x == util.safe_dump(data)


def test_safe_load():
    assert {'foo': 'bar'} == util.safe_load('foo: bar')


def test_safe_load_returns_empty_dict_on_empty_string():
    assert {} == util.safe_load('')


def test_safe_load_exits_when_cannot_parse():
    data = """
---
%foo:
""".strip()

    with pytest.raises(SystemExit) as e:
        util.safe_load(data)

    assert 1 == e.value.code

def test_generate_run_id():
    assert uuid.UUID(util.generate_run_id())


def test_sysexit_with_message(patched_logger_critical):
    with pytest.raises(SystemExit) as e:
        util.sysexit_with_message('foo')

    assert 1 == e.value.code

    patched_logger_critical.assert_called_once_with('foo')


def test_sysexit_with_message_and_custom_code(patched_logger_critical):
    with pytest.raises(SystemExit) as e:
        util.sysexit_with_message('foo', 2)

    assert 2 == e.value.code

    patched_logger_critical.assert_called_once_with('foo')

@responses.activate
def test_request_new_task_id():
    responses.add(responses.POST, 'http://gman_url/gman', json={'task': {'task_id': '1234'}})

    resp = util.request_new_task_id('1234', 'http://gman_url/gman', 'test', 'tests')

    assert resp == '1234'

@responses.activate
def test_wait_for_task_status(gman_events_fixture):

    mock_response_data = [
        {
            'message': 'blank message',
            'status': 'started',
            'thread_id': '',
            'timestamp': '2019-05-16T19:56:33.231452+00:00',
            'task': {
                'project': 'python_project',
                'run_id': '574b1db2-ae55-41bb-8680-43703f3031f2',
                'caller': 'gateway',
                'task_id': '157dee55-819b-4706-8809-f5642ac035e6'
            }
        }
    ]
    responses.add(responses.GET, 'http://gman_url/gman/1234/events', json=mock_response_data)

    resp = util.wait_for_task_status(1234, 'started', 'http://gman_url/gman')

    assert resp
