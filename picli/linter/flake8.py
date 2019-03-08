import requests
import tempfile

from picli.linter import base


class Flake8(base.Base):

    def __init__(self, base_config, config):
        super(Flake8, self).__init__(base_config, config)

    @property
    def name(self):
        return 'flake8'

    @property
    def default_options(self):
        options = self._config.flake8_options

        return options

    @property
    def url(self):
        return super().url

    def zip_files(self, destination):
        return super().zip_files(destination)

    def execute(self):
        super().execute()

