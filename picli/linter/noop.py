from picli.linter import base
from picli import logger

LOG = logger.get_logger(__name__)


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
        LOG.info(f"Executing linter {self.name}")
        for file in self._config.files:
            if file['linter'] == self.name:
                message = f'Executing {self.name} on {file["file"]}'
                LOG.success(message)
