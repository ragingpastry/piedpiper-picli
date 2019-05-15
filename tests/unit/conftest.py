import pytest
import os
import tempfile
import yaml
import mock

from picli import config

@pytest.fixture
def patched_flake8(mocker):
    return mocker.patch('picli.actions.styler.flake8.Flake8.execute')

@pytest.fixture
def patched_style_pipe_config(mocker):
    return mocker.patch('picli.configs.style_pipe')

@pytest.fixture
def gman_events_fixture():

    gman_events = [
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

    return gman_events


@pytest.helpers.register
def piedpiper_ephemeral_directory():
    tempdir = tempfile.TemporaryDirectory()
    return tempdir.name


@pytest.helpers.register
def piedpiper_directories():
    pi_dirs = {
        'piedpiper.d/': {
            'default_vars.d/': {
                'file_vars.d/': None,
                'group_vars.d': None,
                'pipe_vars.d/': None
            },
        }
    }
    return pi_dirs

@pytest.fixture
def group_vars_all_fixture():
    group_vars_all = {
        'pi_style': [
            {
                'name': '*',
                'sast': 'noop'
            }
        ],
        'pi_sast': [
            {
                'name': '*',
                'sast': 'noop',
            }
        ]
    }
    return group_vars_all

@pytest.fixture
def pi_global_vars_fixture():
    pi_global_vars = {
        'pi_global_vars': {
            'project_name': 'python_project',
            'ci_provider': 'gitlab-ci',
            'vars_dir': 'default_vars.d',
            'version': '0.0.0',
            'gman_url': 'http://172.17.0.1:8089/gman',
            'storage': {
                'url': 'http://127.0.0.1:9000',
                'access_key': '1234',
                'secret_key': '1234',
            }

        }
    }
    return pi_global_vars

@pytest.fixture
def pi_pipe_vars_validate_fixture():
    pi_pipe_vars_validate = {
        'pi_validate_pipe_vars': {
            'run_pipe': True,
            'url': 'http://172.17.0.1:8089/function',
            'version': 'latest',
            'policy': {
                'enabled': True,
                'enforcing': True,
                'version': '0.0.0'
            }
        }
    }
    return pi_pipe_vars_validate

@pytest.helpers.register
def write_piedpiper_files(piedpiper_ephemeral_directory,
                          piedpiper_directories,
                          pi_pipe_vars_validate_fixture,
                          pi_global_vars_fixture):
    def create_directories(d, current_dir='./'):
        for key, value in d.items():
            os.makedirs(os.path.join(current_dir, key), exist_ok=True)
            if type(value) == dict:
                create_directories(value, os.path.join(current_dir, key))
    create_directories(piedpiper_directories, piedpiper_ephemeral_directory)
    with open(f'{piedpiper_ephemeral_directory}/piedpiper.d/default_vars.d/pipe_vars.d/pi_validate.yml', 'w') as f:
        f.write(yaml.dump(pi_pipe_vars_validate_fixture()))
    with open(f'{piedpiper_ephemeral_directory}/piedpiper.d/pi_global_vars.yml', 'w') as f:
        f.write(yaml.dump(pi_global_vars_fixture()))


@pytest.fixture
def piedpiper_directory_fixture():
    path = pytest.helpers.piedpiper_ephemeral_directory()
    if not os.path.isdir(path):
        os.makedirs(path)
    pytest.helpers.write_piedpiper_files(path, pytest.helpers.piedpiper_directories(),
                                         pi_pipe_vars_validate_fixture,
                                         pi_global_vars_fixture)
    return f'{path}/piedpiper.d/pi_global_vars.yml'


@pytest.fixture
def patched_logger_critical(mocker):
    return mocker.patch('logging.Logger.critical')


@pytest.fixture
def patched_logger_info(mocker):
    return mocker.patch('logging.Logger.info')


@pytest.fixture
def config_instance(piedpiper_directory_fixture):
    #pytest.helpers.write_piedpiper_files(pytest.helpers.piedpiper_ephemeral_directory, piedpiper_directory_fixture)
    c = config.BaseConfig(piedpiper_directory_fixture, debug=False)
    return c

