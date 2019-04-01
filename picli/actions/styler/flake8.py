from picli.actions import base


class Flake8(base.Base):
    """Flake8 styler implementation

    Defines behaviour for the Flake8 styler.
    Currently this just exists to set the Flake8 name.
    All other methods simply call the superclass methods.
    We override here simply for readability, but that may
    change.

    """

    def __init__(self, pipe_config, run_config):
        super(Flake8, self).__init__(pipe_config, run_config)

    @property
    def name(self):
        return 'flake8'

    @property
    def url(self):
        return super().url

    def zip_files(self, destination):
        return super().zip_files(destination)

    def execute(self):
        super().execute()
