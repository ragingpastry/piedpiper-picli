from picli import util

import glob


class LintConfig(object):

    def __init__(self, config):
        self._config = self._build_config(config)
        self.files = self._build_file_list()

    def _build_config(self, config):
        return util.safe_load(config)

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
