from picli.linter import base
from picli import logger

LOG = logger.get_logger(__name__)


class Noop(base.Base):
    """Noop SAST analyzer implementation

    Performs a noop for all files in our
    configuration which have the "noop" SAST anaylzer. We simply
    print to the screen instead of sending the files anywhere.

    """

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
        LOG.info(f"Executing SAST analyzer: {self.name}")
        for file in self.run_config.files:
            if file['sast'] == self.name:
                message = f'Executing {self.name} on {file["file"]}'
                LOG.success(message)
