from picli.actions import base
from picli import logger

LOG = logger.get_logger(__name__)


class Noop(base.Base):
    """Noop styler implementation

    Performs a noop for all files in our
    configuration which have the "noop" styler. We simply
    print to the screen instead of sending the files anywhere.

    """

    def __init__(self, pipe_config, run_config):
        super(Noop, self).__init__(pipe_config, run_config)

    @property
    def name(self):
        return 'noop'

    @property
    def url(self):
        pass

    def execute(self):
        LOG.info(f"Executing styler {self.name}")
        for file in self.run_config.files:
            message = f'Executing {self.name} on {file["file"]}'
            LOG.success(message)
