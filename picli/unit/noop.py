from picli.unit import base
from picli import logger

LOG = logger.get_logger(__name__)


class Noop(base.Base):
    """Noop unit tester implementation

    Performs a noop for all files in our
    configuration which have the "noop" unit tester. We simply
    print to the screen instead of sending the files anywhere.

    """

    def __init__(self, pipe_config):
        super(Noop, self).__init__(pipe_config)

    @property
    def name(self):
        return 'noop'

    @property
    def url(self):
        pass

    def execute(self):
        LOG.info(f"Executing unit tester {self.name}")
        for file in self.run_config.files:
            if file['unit'] == self.name:
                message = f'Executing {self.name} on {file["file"]}'
                LOG.success(message)
