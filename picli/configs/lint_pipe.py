from picli.configs.base_pipe import BasePipeConfig
from picli.model import lint_pipeconfig_schema
from picli import logger
from picli import util

LOG = logger.get_logger(__name__)


class LintPipeConfig(BasePipeConfig):

    def __init__(self, base_config):
        super(LintPipeConfig, self).__init__(base_config)
        self._validate()

    @property
    def name(self):
        return 'lint'

    def _validate(self):
        errors = lint_pipeconfig_schema.validate(self._pipe_config)
        if errors != True:
            msg = f"Failed to validate Lint Pipe Config. \n\n{errors.messages}"
            util.sysexit_with_message(msg)

    def _dump_configs(self):
        for lint_config in self.run_configs:
            yield util.safe_dump(lint_config.files)
