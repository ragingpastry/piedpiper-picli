from picli import logger
from picli import util

import glob
import os

LOG = logger.get_logger(__name__)


class RunConfig(object):

    def __init__(self, config, base_config):
        self.config = self._build_config(config)
        self.base_config = base_config
        self.files = self._build_file_definitions()

    def _build_config(self, config):
        return util.safe_load(config)

    def _build_file_list(self, group):
        """
        Build a list of files based on the glob pattern given in
        group_vars.d/{pipe}.
        The glob will be applied to a path relative to the specified
        vars directory.
        :return:
        """
        file_glob = group['name']
        file_list = \
            glob.glob(f'{self.base_config.vars_dir}/../../**/{file_glob}',
                      recursive=True)
        if not file_list:
            message = \
                f'File Glob {file_glob} returned nothing ' \
                f'in {self.base_config.vars_dir}/../../'
            LOG.warn(message)

        return file_list

    def _build_file_definitions(self):
        file_definitions = []
        for group in self.config['pi_lint']:
            file_list = self._build_file_list(group)
            file_definition_list = []
            for file in file_list:
                if os.path.isdir(file):
                    continue

                try:
                    file_definition = {
                        'file': os.path.relpath(file,
                                                self.base_config.base_dir),
                        'linter': group['linter']
                    }
                except KeyError as e:
                    message = f"Invalid key found in run_vars.{self.config}" \
                              f"\n\n{e}"
                    util.sysexit_with_message(message)
                file_definition_list.append(file_definition)

            file_definitions.append(file_definition_list)

        return [
            definition
            for element in file_definitions
            for definition in element
        ]
