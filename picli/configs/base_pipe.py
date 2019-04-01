import abc
from itertools import filterfalse
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

    def __init__(self, base_config, debug):
        """
        Builds a BaseConfig object, run configurations,
        and a pipe_config based on the subclasses' name attr.
        :param base_config:
        """
        self.base_config = BaseConfig(base_config, debug)
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
        group_vars_dir = f'{self.base_config.vars_dir}/group_vars.d'

        group_configs = []
        if os.path.isdir(group_vars_dir):
            for root, dirs, files in os.walk(
                    f'{self.base_config.vars_dir}/group_vars.d/'
            ):
                if len(files) == 0:
                    message = f'No group_vars found in {self.base_config.vars_dir}'
                    util.sysexit_with_message(message)
                for file in files:
                    with open(os.path.join(root, file)) as f:
                        group_config = f.read()
                        group_configs.append({'file': file, 'config': util.safe_load(group_config)})
            return group_configs
        else:
            message = f'Failed to read group_vars in {self.base_config.vars_dir}.'
            util.sysexit_with_message(message)

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
                    file_name = os.path.join(root, file)
                    with open(file_name) as f:
                        file_config = f.read()
                        yield (file_config, file_name)

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
            for step, config in group['config'].items():
                if step == f'pi_{self.name}':
                    run_config = RunConfig(group['file'], config, self.base_config)
                    for file_definition in run_config.files:
                        for file, file_name in self._read_file_vars():
                            file_config = util.safe_load(file)
                            try:
                                if file_definition['file'] == file_config['file']:
                                    file_definition.update(file_config)
                            except KeyError as e:
                                message = f'Invalid file_vars config in {file_name}. \n\nInvalid Key: {e}'
                                util.sysexit_with_message(message)
                    group_configs.append(run_config)
                elif self.name == 'validate':
                    run_config = RunConfig(group['file'], config, self.base_config)
                    for file_definition in run_config.files:
                        for file, file_name in self._read_file_vars():
                            file_config = util.safe_load(file)
                            try:
                                if file_definition['file'] == file_config['file']:
                                    file_definition.update(file_config)
                            except KeyError as e:
                                message = f'Invalid file_vars config in {file_name}. \n\nInvalid Key: {e}'
                                util.sysexit_with_message(message)
                    group_configs.append(run_config)
        if not len(group_configs):
            message = f'No group configs found for pi_{self.name} in {self.base_config.vars_dir}/group_vars.d/'
            util.sysexit_with_message(message)

        return group_configs

    def _build_run_config(self):
        """
        Returns a single merged RunConfig object for further
        steps to use.
        :return: RunConfig object
        """
        run_configs = self._build_group_configs()
        run_config = self._merge_run_configs(run_configs)
        return run_config

    def _merge_run_configs(self, run_configs):
        """
        Merge run configurations into a single RunConfig object which will be used
        by a subcommand's execute function.

        Merge all run_config.files into the first run_config.files object.
        :param run_configs: List of RunConfig objects build from reading group_vars.d
        :return: RunConfig object
        """
        default_run_configs = [
            rc_default for rc_default in run_configs
            if rc_default.name == 'all.yml']
        other_run_configs = [
            rc_other for rc_other in run_configs
            if rc_other.name != 'all.yml']
        for run_config in default_run_configs:
            run_config.files[:] = filterfalse(
                lambda x: x in [
                    file for rc in other_run_configs
                    for file in rc.files
                ], run_config.files)
        return run_configs

    @property
    def debug(self):
        return self.base_config.debug

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

    def dump_configs(self):
        run_config = {}
        file_config = [file for run_config in self.run_config for file in run_config.files]
        util.merge_dicts(run_config, {'file_config': file_config})
        util.merge_dicts(run_config, self.base_config.config)
        util.merge_dicts(run_config, self.pipe_config)
        return util.safe_dump(run_config)
