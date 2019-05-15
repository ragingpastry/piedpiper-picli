from picli import logger
from picli import util

import glob
import os

LOG = logger.get_logger(__name__)


class RunConfig(object):

    def __init__(self, name, config, base_config):
        self.config = config
        self.name = name
        self.base_config = base_config
        self.files = self._build_file_definitions()

    def _build_file_list(self, group):
        """
        Build a list of files based on the glob pattern given in
        group_vars.d/{pipe}.
        The glob will be applied to a path relative to the specified
        vars directory.
        :return:
        """
        try:
            file_glob = group['name']
        except KeyError as e:
            message = f'Invalid group_vars file found. \n{e}'
            util.sysexit_with_message(message)
        file_list = \
            glob.glob(f'{self.base_config.base_dir}/{file_glob}', recursive=True)
        if not file_list:
            message = \
                f'File Glob {file_glob} returned nothing ' \
                f'in {self.base_config.base_dir}'
            LOG.warn(message)

        return file_list

    def _build_file_definitions(self):
        file_definitions = []
        for config in self.config:
            file_list = self._build_file_list(config)
            file_definition_list = []
            for file in file_list:
                if os.path.isdir(file):
                    continue
                file_definition = {
                    'file': file,
                }
                file_definition_list.append(file_definition)

            file_definitions.append(file_definition_list)

        return [
            definition
            for element in file_definitions
            for definition in element
        ]
