from picli.actions import base


class Cpplint(base.Base):
    """CppLint styler implementation

    Defines behaviour for the cpplint styler.
    Currently this just exists to set the cpplint name.
    All other methods simply call the superclass methods.
    We override here simply for readability, but that may
    change.

    """

    def __init__(self, pipe_config, run_config):
        super(Cpplint, self).__init__(pipe_config, run_config)

    @property
    def name(self):
        return 'cpplint'

    @property
    def url(self):
        return super().url

    def zip_files(self, destination):
        return super().zip_files(destination)

    def execute(self):
        super().execute()
