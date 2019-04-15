import abc
import picli
from picli import logger
from picli import util

LOG = logger.get_logger(__name__)


class Base(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, base_config, debug):
        self._base_config = base_config
        self.debug = debug

    @abc.abstractmethod
    def execute(self):
        pass

    def print_info(self):
        message = f"Action: {self.__class__.__name__}"
        LOG.info(message)


def execute_subcommand(config, subcommand, debug):
    """
    Dynamically discover a subcommand module and class based on
    the subcommand we are executing.
    After discovery, initialize and run the execute method
    on the discovered command object.
    :param config: Configuration file
    :param subcommand: The subcommand we are executing
    :param debug: boolean
    :return:
    """
    command_module = getattr(picli.command, subcommand)
    command = getattr(command_module, util.camelize(subcommand))

    return command(config, debug).execute()


def get_sequence(step):

    if step == 'validate':
        return [
            'validate'
        ]
    elif step == 'style':
        return [
            'style'
        ]
    elif step == 'lint':
        return [
            'validate',
            'style',
            'sast'
        ]
    elif step == 'sast':
        return [
            'sast'
        ]
    else:
        util.sysexit_with_message(f"picli sequence not found for {step}")
