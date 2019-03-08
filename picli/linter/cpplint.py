from picli.linter import base


class Cpplint(base.Base):

    def __init__(self, base_config, config):
        super(Cpplint, self).__init__(base_config, config)

    @property
    def name(self):
        return 'cpplint'

    @property
    def default_options(self):
        options = self._config.cpplint_options

        return options

    @property
    def url(self):
        return super().url

    def zip_files(self, destination):
        return super().zip_files(destination)

    def execute(self):
        super().execute()
