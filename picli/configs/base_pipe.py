import abc
import os

from picli.config import BaseConfig
from picli.configs.run_config import RunConfig
from picli import util


class BasePipeConfig(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, base_config):
        self._base_config = BaseConfig(base_config)
        self.run_config = self._build_run_config()
        self._pipe_config = self._build_pipe_config()

    def _build_pipe_config(self):
        """
        Read pipe_vars.d for configuration file for the pipe.
        Each child class will have its own pi_{self.name}.yml file located in
        {vars_dir}/pipe_vars.d/ which will be read during creation of the child class object.

        :return: Configuration dictionary for the pipe
        """
        try:
            with open(f'{self._base_config.vars_dir}/pipe_vars.d/pi_{self.name}.yml') as config:
                return util.safe_load(config)
        except IOError as e:
            message = f"Failed to parse pi_{self.name}.yml. \n\n{e}"
            util.sysexit_with_message(message)

    def _read_group_vars(self):
        group_configs = []
        for root, dirs, files in os.walk(f'{self._base_config.vars_dir}/group_vars.d/'):
            for file in files:
                if file == 'all.yml':
                    with open(os.path.join(root, file)) as f:
                        group_config = f.read()
                        group_configs.append(group_config)
        for root, dirs, files in os.walk(f'{self._base_config.vars_dir}/group_vars.d/'):
            for file in files:
                if file == 'all.yml':
                    continue
                with open(os.path.join(root, file)) as f:
                    group_config = f.read()
                    group_configs.append(group_config)

        return group_configs

    def _read_file_vars(self):
        for root, dirs, files in os.walk(f'{self._base_config.vars_dir}/file_vars.d/'):
            for file in files:
                with open(os.path.join(root, file)) as f:
                    file_config = f.read()
                    yield file_config

    def _build_group_configs(self):
        group_configs = []
        for group in self._read_group_vars():
            run_config = RunConfig(group, self._base_config)
            for file_definition in run_config.files:
                for file in self._read_file_vars():
                    file_config = util.safe_load(file)
                    if file_definition['file'] == file_config['pi_lint']['file']:
                        file_definition['linter'] = file_config['pi_lint']['linter']
            group_configs.append(run_config)
        return group_configs

    def _build_run_config(self):
        group_configs = self._build_group_configs()
        run_config = self._merge_run_configs(group_configs)
        return run_config

    def _merge_run_configs(self, run_configs):
        """
        Merge run configurations into a single RunConfig object which will be used
        by a subcommand's execute function.
        :param run_configs: List of RunConfig objects build from reading group_vars.d
        :return: RunConfig object
        """
        # Set new_run_config equal to first run_config
        new_run_config = run_configs[0]
        # Loop over run configs starting at the 2nd
        for run_config in run_configs[1:]:
            # For every file in current run_config
            for current_config_file in run_config.files:
                # If the file is not in new_run_config.files list
                if current_config_file['file'] not in [file['file'] for file in new_run_config.files]:
                    # append to new_run_config
                    new_run_config.files.append(current_config_file)
                # Loop over new_run_config files
                for new_config_file in new_run_config.files:
                    # Set overwrite linter if the current_config_file is in the new_config file list
                    if current_config_file['file'] == new_config_file['file']:
                        new_config_file['linter'] = current_config_file['linter']
        return new_run_config

    @property
    @abc.abstractmethod
    def name(self):
        pass

    @property
    def run_pipe(self):
        return self._pipe_config[f'pi_{self.name}_pipe_vars']['run_pipe']

    @property
    def endpoint(self):
        return self._pipe_config[f'pi_{self.name}_pipe_vars']['url']
