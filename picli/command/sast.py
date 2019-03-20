import click
from picli.command import base
from picli.configs.sast_pipe import SastPipeConfig
from picli import logger
from picli import util
import importlib

LOG = logger.get_logger(__name__)


class Sast(base.Base):
    def __init__(self, base_config):
        super(Sast, self).__init__(base_config)

    def execute(self):
        self.print_info()
        sast_pipe_config = SastPipeConfig(self._base_config)
        if sast_pipe_config.run_pipe:
            sast_analyzers = set()
            for file in sast_pipe_config.run_config.files:
                sast_analyzers.add(file['sast'])
            for sast_analyzer in sorted(sast_analyzers):
                sast_module = getattr(
                    importlib.import_module(
                        f'picli.sast.{sast_analyzer}'
                    ),
                    f'{util.camelize(sast_analyzer)}'
                )
                sast = sast_module(sast_pipe_config, sast_pipe_config.run_config)
                sast.execute()
        else:
            LOG.warn("SAST step not enabled.\n\nSkipping...")


@click.command()
@click.pass_context
def sast(context):
    config_file = context.obj.get('args')['config']
    sequence = base.get_sequence('sast')
    for action in sequence:
        base.execute_subcommand(config_file, action)
