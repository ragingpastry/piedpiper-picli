from picli.configs.base_pipe import BasePipeConfig
from picli.model import sast_pipeconfig_schema
from picli import logger
from picli import util


LOG = logger.get_logger(__name__)


class SastPipeConfig(BasePipeConfig):
    """A class to pass configuration to a SAST analyzer

    Subclasses BasePipeConfig.

    An instantiated LintPipeConfig object will contain
    all required properties and files needed by a SAST analyzer
    to execute a lint step. The Lint PipeConfig object will
    do the followinng:
      - Build a BaseConfig object using the file specified
        during initialization.
      - Build a run configuration which contains a list of
        files definitions.
      - Read the SAST analyzer configuration file located in
        {base_dir}/piedpiper.d/{vars_dir}/pipe_vars.d/pi_lint.yml
    """

    def __init__(self, base_config, debug):
        """
        Call the superclass init to build BaseConfig object,
        pipe_configs, and run_configs, then validate.
        :param base_config:
        """
        super(SastPipeConfig, self).__init__(base_config, debug)
        self._validate()

    @property
    def name(self):
        return 'sast'

    def _validate(self):
        errors = sast_pipeconfig_schema.validate(self.pipe_config)
        if errors:
            msg = f"Failed to validate SAST Pipe Config. \n\n{errors.messages}"
            util.sysexit_with_message(msg)
