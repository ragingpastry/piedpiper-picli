import abc
import picli
from picli import logger
from picli import util

LOG = logger.get_logger(__name__)


class Base(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, base_config):
        self._base_config = base_config

    @abc.abstractmethod
    def execute(self):
        pass

    def print_info(self):
        message = f"Action: {self.__class__.__name__}"
        LOG.info(message)


def execute_subcommand(config, subcommand):
    command_module = getattr(picli.command, subcommand)
    command = getattr(command_module, util.camelize(subcommand))

    return command(config).execute()


def get_sequence():

    return [
        'validate',
        'lint'
    ]
