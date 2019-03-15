from picli.configs.base_pipe import BasePipeConfig
from picli.model import lint_pipeconfig_schema
from picli import logger
from picli import util


LOG = logger.get_logger(__name__)


class LintPipeConfig(BasePipeConfig):
    """A class to pass configuration to a Linter

    Subclasses BasePipeConfig.

    An instantiated LintPipeConfig object will contain
    all required properties and files needed by a linter
    to execute a lint step. The Lint PipeConfig object will
    do the followinng:
      - Build a BaseConfig object using the file specified
        during initialization.
      - Build a run configuration which contains a list of
        files definitions.
      - Read the lintpipe configuration file located in
        {base_dir}/piedpiper.d/{vars_dir}/pipe_vars.d/pi_lint.yml
    """

    def __init__(self, base_config):
        """
        Call the superclass init to build BaseConfig object,
        pipe_configs, and run_configs, then validate.
        :param base_config:
        """
        super(LintPipeConfig, self).__init__(base_config)
        self._validate()

    @property
    def name(self):
        return 'lint'

    def _validate(self):
        errors = lint_pipeconfig_schema.validate(self.pipe_config)
        if errors:
            msg = f"Failed to validate Lint Pipe Config. \n\n{errors.messages}"
            util.sysexit_with_message(msg)

    def _dump_configs(self):
        """
        Dump file configurations in the LintPipe's run configuration
        :return: Iterator
        """
        for lint_config in self.run_configs:
            yield util.safe_dump(lint_config.files)
