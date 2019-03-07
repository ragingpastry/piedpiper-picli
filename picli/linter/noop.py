from picli.linter import base


class Noop(base.Base):

    def __init__(self, base_config, config):
        super(Noop, self).__init__(base_config, config)

    @property
    def name(self):
        return 'noop'

    @property
    def default_options(self):
        pass

    @property
    def url(self):
        pass

    def execute(self):
        print('Noop executed on file.')
