from picli.styler import base


class Cpplint(base.Base):
    """CppLint styler implementation

    Defines behaviour for the cpplint styler.
    Currently this just exists to set the cpplint name.
    All other methods simply call the superclass methods.
    We override here simply for readability, but that may
    change.

    """

    def __init__(self, base_config, config):
        super(Cpplint, self).__init__(base_config, config)

    @property
    def name(self):
        return 'cpplint'

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
