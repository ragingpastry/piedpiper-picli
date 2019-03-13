from picli.configs.base_pipe import BasePipeConfig
from picli import configs
from picli.model import validate_pipeconfig_schema
from picli import logger
from picli import util

import importlib

LOG = logger.get_logger(__name__)


class ValidatePipeConfig(BasePipeConfig):
    def __init__(self, base_config):
        super(ValidatePipeConfig, self).__init__(base_config)
        self.pipe_configs = self._build_pipe_configs(base_config)
        self._validate()

    @property
    def name(self):
        return 'validate'

    @property
    def policy_checks_enforcing(self):
        return self._pipe_config['pi_validate_pipe_vars']['policy_checks']['enforcing']

    @property
    def policy_checks_enabled(self):
        return self._pipe_config['pi_validate_pipe_vars']['policy_checks']['enabled']

    def _validate(self):
        errors = validate_pipeconfig_schema.validate(self._pipe_config)
        if errors != True:
            msg = f"Failed to validate Validate Pipe Config. \n\n{errors.messages}"
            util.sysexit_with_message(msg)

    def read_ci_provider_config_file(self):
        return {
            'ci_provider': self._base_config.ci_provider,
            'ci_provider_config':
                util.safe_load_file(f'{self._base_config.piedpiper_dir}/{self._base_config.ci_provider_file}')
        }

    def _build_pipe_configs(self, base_config):
        pipes = [pipe for pipe in dir(configs)
                 if "_pipe" in pipe and
                 "validate" not in pipe and
                 "base" not in pipe]
        for pipe in pipes:
            pipe_config_module = getattr(importlib.import_module(f'picli.configs.{pipe}'),
                                         f'{util.camelize(pipe)}Config')
            pipe_config = pipe_config_module(base_config)
            yield pipe_config

    def dump_configs(self):
        run_config = {}
        file_config = [file for file in self.run_config.files]
        util.merge_dicts(run_config, {'file_config': file_config})
        util.merge_dicts(run_config, self._base_config._config)
        util.merge_dicts(run_config, self._pipe_config)
        util.merge_dicts(run_config, {'ci': self.read_ci_provider_config_file()})
        for pipe_config in self.pipe_configs:
            util.merge_dicts(run_config, pipe_config._pipe_config)

        return util.safe_dump(run_config)
