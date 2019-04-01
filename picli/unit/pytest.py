from picli.unit import base


class Pytest(base.Base):
    """Pytest Unit Tester implementation

    Defines behaviour for the Unit Tester.
    Currently this just exists to set the unit tester name.
    All other methods simply call the superclass methods.
    We override here simply for readability, but that may
    change.

    """

    def __init__(self, pipe_config, run_config):
        super(Pytest, self).__init__(pipe_config, run_config)

    @property
    def name(self):
        return 'pytest'

    @property
    def url(self):
        return super().url

    def zip_files(self, destination):
        return super().zip_files(destination)

    def execute(self):
        super().execute()
