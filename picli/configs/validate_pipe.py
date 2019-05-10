from picli.configs.base_pipe import BasePipeConfig
from picli import configs
from picli.model import validate_pipeconfig_schema
from picli import logger
from picli import util

import importlib
from functools import reduce
import operator

LOG = logger.get_logger(__name__)


class ValidatePipeConfig(BasePipeConfig):
    """Configuration class for the validation step

    Build a list of all valid PipeConfig objects and provides
    a method for dumping the configuration of all associated objects.

    Subclasses BasePipeConfig.
    """

    def __init__(self, base_config):
        """
        Initialize a ValidatePipeConfig object and returns None.
        :param base_config:
        """
        super(ValidatePipeConfig, self).__init__(base_config)
        self.pipe_configs = self._build_pipe_configs(base_config)
        self._validate()

    @property
    def name(self):
        return 'validate'

    @property
    def pipe_vars(self):
        return self.pipe_config['pi_validate_pipe_vars']

    @property
    def policy_enforcing(self):
        return self.pipe_vars['policy']['enforcing']

    @property
    def policy_enabled(self):
        return self.pipe_vars['policy']['enabled']

    @property
    def policy_version(self):
        return self.pipe_vars['policy']['version']

    def _validate(self):
        errors = validate_pipeconfig_schema.validate(self.pipe_config)
        if errors:
            msg = f"Failed to validate Validate Pipe Config. \n\n{errors.messages}"
            util.sysexit_with_message(msg)

    def read_ci_provider_file(self):
        """
        Build a CI provider configuration dict.

        FIXME: This should probably be moved into the config.py namespace
        :return: dict
        """
        return {
            'ci_provider': self.base_config.ci_provider,
            'ci_provider_config':
                util.safe_load_file(self.base_config.ci_provider_file)
        }

    def _build_pipe_configs(self, base_config):
        """
        Builds a list of PipeConfig objects based on
        the contents of the picli.configs package directory so
        that we can dump their configurations for the validation
        function to use.
        We ignore the validate and base PipeConfig classes
        because we already have those instantiated.
        :param base_config:
        :return: iterator
        """
        pipe_configs = []
        pipes = [pipe for pipe in dir(configs)
                 if "_pipe" in pipe and
                 "validate" not in pipe and
                 "base" not in pipe]
        for pipe in pipes:
            pipe_config_module = getattr(importlib.import_module(f'picli.configs.{pipe}'),
                                         f'{util.camelize(pipe)}Config')
            pipe_config = pipe_config_module(base_config)
            pipe_configs.append(pipe_config)

        return pipe_configs

    def dump_configs(self):
        """
        Create a single dictionary of variables which
        display how PiCli was configured at the time of the run.
        This will be used by a validation function to ensure that
        the configuration of PiCli was correct according to an
        external source.
        :return: dict
        """
        merged_run_configs = {}
        file_configs = []
        group_configs = []
        util.merge_dicts(merged_run_configs, self.base_config.config)
        util.merge_dicts(merged_run_configs, self.pipe_config)
        util.merge_dicts(merged_run_configs, {'ci': self.read_ci_provider_file()})
        for pipe_config in self.pipe_configs:
            group_config = [group_config
                            for run_config in pipe_config.run_config
                            for group_config in run_config.config]
            group_configs.append(group_config)
            file_config = [file
                           for run_config in pipe_config.run_config
                           for file in run_config.files]
            file_configs.append(file_config)
            util.merge_dicts(merged_run_configs, pipe_config.pipe_config)

        util.merge_dicts(
            merged_run_configs,
            {'group_configs': reduce(operator.concat, group_configs)}
        )
        util.merge_dicts(
            merged_run_configs,
            {'file_configs': reduce(operator.concat, file_configs)}
        )

        return util.safe_dump(merged_run_configs)
