import abc
import glob
from picli import util
import os
import yaml


class BaseConfig(object):

    def __init__(self, config):
        self._config = self._read_config(config)
        self.lint_config = self.build_lint_config()

    def build_lint_config(self):
        for group in self._read_group_vars():
            lint_config = LintConfig(group)
            for file_definition in lint_config.files:
                for file in self._read_file_vars():
                    file_config = yaml.load(file)
                    if file_definition['file'] == file_config['pi_lint']['file']:
                        file_definition['linter'] = file_config['pi_lint']['linter']
            yield lint_config

    def _read_config(self, config):
        with open(config) as c:
            return yaml.load(c)

    @staticmethod
    def _read_group_vars():
        for root, dirs, files in os.walk('group_vars.d/'):
            for file in files:
                with open(os.path.join(root, file)) as f:
                    group_config = f.read()
                    yield group_config

    @staticmethod
    def _read_file_vars():
        for root, dirs, files in os.walk('file_vars.d/'):
            for file in files:
                with open(os.path.join(root, file)) as f:
                    file_config = f.read()
                    yield file_config

    def write_config(self):
        util.render_runvars(self)


class LintConfig(BaseConfig):

    def __init__(self, config):
        self._config = self._build_config(config)
        self.files = self._build_file_list()

    def _build_config(self, config):
        return yaml.load(config)

    def _build_file_list(self):
        file_definition_list = []
        file_glob = self._config['pi_lint']['name']
        file_list = glob.glob(f'**/{file_glob}', recursive=True)
        for file in file_list:
            file_definition = {
                'file': file,
                'linter': self.linter
            }
            file_definition_list.append(file_definition)

        return file_definition_list

    @property
    def linter(self):
        return self._config['pi_lint']['linter']

    def write_config(self):
        pass

