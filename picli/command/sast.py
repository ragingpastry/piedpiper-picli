import click
from picli.command import base
from picli.config import BaseConfig
from picli.configs.sast_pipe import SastPipeConfig
from picli import logger
from picli import util
import importlib

LOG = logger.get_logger(__name__)


class Sast(base.Base):
    def __init__(self, config):
        super(Sast, self).__init__(config)

    def execute(self):
        self.print_info()
        sast_pipe_config = SastPipeConfig(self.base_config)
        if sast_pipe_config.run_pipe:
            for run_config in sast_pipe_config.run_config:
                sast_module = getattr(
                    importlib.import_module(
                        f'picli.actions.sast.{run_config.config[0]["sast"]}'
                    ),
                    f'{util.camelize(run_config.config[0]["sast"])}'
                )
                sast_analyzer = sast_module(sast_pipe_config, run_config)
                sast_analyzer.execute()
        else:
            LOG.warn("SAST step not enabled.\n\nSkipping...")


@click.command()
@click.pass_context
def sast(context):
    debug = context.obj.get('args')['debug']
    config = BaseConfig(context.obj.get('args')['config'], debug)
    sequence = base.get_sequence('sast')
    base.execute_sequence(sequence, config)

