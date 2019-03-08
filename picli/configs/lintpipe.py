import os

from picli.configs.basepipe import PipeConfig
from picli.configs.lintconfig import LintConfig
from picli import util


class LintPipeConfig(PipeConfig):

    def __init__(self, base_config):
        super(LintPipeConfig, self).__init__(base_config)
        self.lint_configs = self._build_lint_configs()

    @property
    def name(self):
        return 'lint'

    def _read_group_vars(self):
        for root, dirs, files in os.walk(f'piedpiper.d/{self.vars_dir}/group_vars.d/'):
            for file in files:
                with open(os.path.join(root, file)) as f:
                    group_config = f.read()
                    yield group_config

    def _read_file_vars(self):
        for root, dirs, files in os.walk(f'piedpiper.d/{self.vars_dir}/file_vars.d/'):
            for file in files:
                with open(os.path.join(root, file)) as f:
                    file_config = f.read()
                    yield file_config

    def _build_lint_configs(self):
        for group in self._read_group_vars():
            lint_config = LintConfig(group)
            for file_definition in lint_config.files:
                for file in self._read_file_vars():
                    file_config = util.safe_load(file)
                    if file_definition['file'] == file_config['pi_lint']['file']:
                        file_definition['linter'] = file_config['pi_lint']['linter']
            yield lint_config
