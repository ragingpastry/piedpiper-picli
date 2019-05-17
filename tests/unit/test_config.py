import mock
import tempfile
import pytest
import yaml
import os
from marshmallow import ValidationError

import picli
from picli import config


@pytest.fixture
def default_state_fixture():
    default_state = {
        'validate': {}
    }

    return default_state


def test_config_instance(config_instance):

    assert isinstance(config_instance, config.BaseConfig)


def test_state_file(config_instance):

    state_directory = '/tmp/piedpiper/python_project/.pi_state.yml'

    assert config_instance._state_file == state_directory


def test_state_directory(config_instance):
    state_directory = '/tmp/piedpiper/python_project'

    assert config_instance.state_directory == state_directory


def test_create_state_file(config_instance):
    assert os.path.isfile(config_instance._state_file)


def test_create_state(config_instance, default_state_fixture):
    config_instance._create_state()

    with open(config_instance._state_file) as f:
        written_state = yaml.load(f.read())

    assert default_state_fixture == written_state


def test_read_state(config_instance):
    with mock.patch('picli.util.safe_load_file') as mock_load:
        config_instance.read_state()

    mock_load.assert_called_once_with('/tmp/piedpiper/python_project/.pi_state.yml')


def test_find_base_dir(config_instance):
    base_dir = '/tmp'

    assert config_instance._find_base_dir('/tmp/piedpiper.d/pi_global_vars.yml') == base_dir


def test_read_config(config_instance, pi_global_vars_fixture):
    test_config = tempfile.NamedTemporaryFile()
    with open(test_config.name, 'w') as f:
        f.write(yaml.dump(pi_global_vars_fixture))

    assert config_instance._read_config(test_config.name) == pi_global_vars_fixture


def test_read_config_error(config_instance):
    with mock.patch('picli.util.sysexit_with_message') as mock_exit:
        config_instance._read_config('does_not_exist')
        mock_exit.assert_called_once()


def test_validate(config_instance):
    assert config_instance._validate() is None


def test_validate_error(config_instance):
    with mock.patch('picli.util.sysexit_with_message') as mock_exit:
        with mock.patch('picli.model.base_schema.validate', mock.MagicMock(return_value=ValidationError('yes'))):
            config_instance._validate()
            mock_exit.assert_called_once()


def test_global_vars(config_instance, pi_global_vars_fixture):
    assert config_instance.global_vars == pi_global_vars_fixture['pi_global_vars']


def test_vars_dir(config_instance):
    assert os.path.isdir(config_instance.vars_dir)


def test_invalid_vars_dir(config_instance):
    with mock.patch('picli.util.sysexit_with_message') as mock_exit:
        with mock.patch('picli.config.os.path.isdir', mock.MagicMock(return_value=False)):
            directory = config_instance.vars_dir
            mock_exit.assert_called_once()


def test_base_dir(config_instance):
    assert os.path.isdir(config_instance.base_dir)


def test_piedpiper_dir(config_instance):
    assert os.path.isdir(config_instance.piedpiper_dir)


def test_invalid_piedpiper_dir(config_instance):
    with mock.patch('picli.util.sysexit_with_message') as mock_exit:
        with mock.patch('picli.config.os.path.isdir', mock.MagicMock(return_value=False)):
            config_instance._set_piedpiper_dir()
            mock_exit.assert_called_once()


def test_storage(config_instance):
    storage_default = {
        'url': 'http://127.0.0.1:9000',
        'access_key': '1234',
        'secret_key': '1234'
    }
    assert config_instance.storage == storage_default


def test_gman_url(config_instance):
    gman_url = 'http://172.17.0.1:8089/gman'

    assert config_instance.gman_url == gman_url


def test_ci_provider(config_instance):
    ci_provider = 'gitlab-ci'

    assert config_instance.ci_provider == ci_provider


def test_ci_provider_file(config_instance):
    ci_provider_file = '.gitlab-ci.yml'

    assert os.path.basename(config_instance.ci_provider_file) == ci_provider_file


def test_update_state(config_instance):
    updated_state = {
        'validate': {},
        'run_id': '1234'
    }

    config_instance.update_state(updated_state)

    assert config_instance.read_state() == updated_state


def test_version(config_instance):
    version = '0.0.0'

    assert config_instance.version == version


def test_config_instance_generates_run_id(piedpiper_directory_fixture):
    run_id = '1234'
    with mock.patch('picli.util.generate_run_id', mock.MagicMock(return_value=run_id)) as mock_generate:
        c = config.BaseConfig(piedpiper_directory_fixture, debug=False)
        mock_generate.assert_called_once()
        assert c.run_id == '1234'


def test_config_debug_displays_run_id_state(piedpiper_directory_fixture, patched_logger_info):
    run_id = '1234'
    run_id_state = {
        'run_id': run_id
    }
    with mock.patch('picli.util.generate_run_id', mock.MagicMock(return_value=run_id)) as mock_generate:
        c = config.BaseConfig(piedpiper_directory_fixture, debug=True)

        assert patched_logger_info.called_once_with(picli.util.safe_dump(run_id_state))




