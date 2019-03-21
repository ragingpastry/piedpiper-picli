import abc
import os

from picli.config import BaseConfig
from picli.configs.run_config import RunConfig
from picli import util


class BasePipeConfig(object):
    """Abstract Base class for all pipes
    Ties together common functionality and required
    attributes between all pipes.

    Not to be created directly. Must be subclassed.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, base_config):
        """
        Builds a BaseConfig object, run configurations,
        and a pipe_config based on the subclasses' name attr.
        :param base_config:
        """
        self.base_config = BaseConfig(base_config)
        self.run_config = self._build_run_config()
        self.pipe_config = self._build_pipe_config()

    def _build_pipe_config(self):
        """
        Read pipe_vars.d for configuration file for the pipe.
        Each child class will have its own pi_{self.name}.yml file located in
        {vars_dir}/pipe_vars.d/ which will be read during
        creation of the child class object.

        :return: Configuration dictionary for the pipe
        """
        try:
            with open(
                f'{self.base_config.vars_dir}/pipe_vars.d/pi_{self.name}.yml'
            ) as config:
                return util.safe_load(config)
        except IOError as e:
            message = f"Failed to parse pi_{self.name}.yml. \n\n{e}"
            util.sysexit_with_message(message)

    def _read_group_vars(self):
        """
        Read all files in {base_dir}/piedpiper.d/{vars_dir}/group_vars.d/
        and returns a list of variable configurations. We first parse all.yml
        if it exists so that it is the first item in the list. This allows for
        the other group_vars files to override the values in all.yml
        :return: list
        """

        group_configs = []
        if os.path.isdir(f'{self.base_config.vars_dir}/group_vars.d/'):
            for root, dirs, files in os.walk(
                    f'{self.base_config.vars_dir}/group_vars.d/'
            ):
                if len(files) == 0:
                    message = f'group_vars is blank in {self.base_config.vars_dir}'
                    util.sysexit_with_message(message)
                for file in files:
                    if file == 'all.yml':
                        with open(os.path.join(root, file)) as f:
                            group_config = f.read()
                            group_configs.append(group_config)
        else:
            message = f'Failed to read group_vars in {self.base_config.vars_dir}.'
            util.sysexit_with_message(message)

        for root, dirs, files in os.walk(
                f'{self.base_config.vars_dir}/group_vars.d/'
        ):
            if len(files) == 0:
                message = f'No group_vars found in {self.base_config.vars_dir}'
                util.sysexit_with_message(message)
            for file in files:
                if file == 'all.yml':
                    continue
                with open(os.path.join(root, file)) as f:
                    group_config = f.read()
                    group_configs.append(group_config)
        return group_configs

    def _read_file_vars(self):
        """
        Read all files in {base_dir}/piedpiper.d/{vars_dir}/files_vars.d/
        :return: iterator
        """
        if os.path.isdir(f'{self.base_config.vars_dir}/file_vars.d/'):
            for root, dirs, files in os.walk(
                    f'{self.base_config.vars_dir}/file_vars.d/'
            ):
                for file in files:
                    with open(os.path.join(root, file)) as f:
                        file_config = f.read()
                        yield file_config

        else:
            message = f"Failed to read file_vars.d in {self.base_config.vars_dir}/file_vars.d/."
            util.sysexit_with_message(message)

    def _build_group_configs(self):
        """
        Performs the merging of variables defined in file_vars with
        those found in group_vars. The inspiration for this
        functionality was taken from Ansible's group_vars and file_vars.
        If a file definition exists in file_vars.d/ that also exists
        in a group_vars RunConfig, we overwrite the group_vars RunConfig
        variable with the one found in file_vars.
        :return: list
        """
        group_configs = []
        for group in self._read_group_vars():
            run_config = RunConfig(group, self.base_config)
            for file_definition in run_config.files:
                for file in self._read_file_vars():
                    file_config = util.safe_load(file)
                    if file_definition['file'] == file_config['pi_lint']['file']:
                        file_definition['linter'] = file_config['pi_lint']['linter']
            group_configs.append(run_config)
        return group_configs

    def _build_run_config(self):
        """
        Returns a single merged RunConfig object for further
        steps to use.
        :return: RunConfig object
        """
        group_configs = self._build_group_configs()
        run_config = self._merge_run_configs(group_configs)
        return run_config

    def _merge_run_configs(self, run_configs):
        """
        Merge run configurations into a single RunConfig object which will be used
        by a subcommand's execute function.

        Merge all run_config.files into the first run_config.files object.
        :param run_configs: List of RunConfig objects build from reading group_vars.d
        :return: RunConfig object
        """
        merged_run_config = run_configs[0]
        for run_config in run_configs[1:]:
            for run_config_file in run_config.files:
                if run_config_file['file'] not in [file['file']
                                                   for file in merged_run_config.files]:
                    merged_run_config.files.append(run_config_file)
                for merged_config_file in merged_run_config.files:
                    if run_config_file['file'] == merged_config_file['file']:
                        merged_config_file.update(run_config_file)
        return merged_run_config

    @property
    @abc.abstractmethod
    def name(self):
        pass

    @property
    def run_pipe(self):
        return self.pipe_config[f'pi_{self.name}_pipe_vars']['run_pipe']

    @property
    def endpoint(self):
        return self.pipe_config[f'pi_{self.name}_pipe_vars']['url']

    @property
    def version(self):
        return self.pipe_config[f'pi_{self.name}_pipe_vars']['version']
