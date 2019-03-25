from picli.sast import base


class Cppcheck(base.Base):
    """Cppcheck SAST analyzer implementation

    Defines behaviour for the cppcheck SAST analyzer.
    Currently this just exists to set the cppcheck name.
    All other methods simply call the superclass methods.
    We override here simply for readability, but that may
    change.

    """

    def __init__(self, base_config, config):
        super(Cppcheck, self).__init__(base_config, config)

    @property
    def name(self):
        return 'cppcheck'

    @property
    def default_options(self):
        options = self.run_config.cpplint_options

        return options

    @property
    def url(self):
        return super().url

    def zip_files(self, destination):
        return super().zip_files(destination)

    def execute(self):
        super().execute()
