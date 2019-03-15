from picli.linter import base


class Flake8(base.Base):
    """Flake8 linter implementation

    Defines behaviour for the Flake8 linter.
    Currently this just exists to set the Flake8 name.
    All other methods simply call the superclass methods.
    We override here simply for readability, but that may
    change.

    """

    def __init__(self, base_config, config):
        super(Flake8, self).__init__(base_config, config)

    @property
    def name(self):
        return 'flake8'

    @property
    def default_options(self):
        options = self.run_config.flake8_options

        return options

    @property
    def url(self):
        return super().url

    def zip_files(self, destination):
        return super().zip_files(destination)

    def execute(self):
        super().execute()
