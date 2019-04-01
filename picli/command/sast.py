import click
from picli.command import base
from picli.configs.sast_pipe import SastPipeConfig
from picli import logger
from picli import util
import importlib

LOG = logger.get_logger(__name__)


class Sast(base.Base):
    def __init__(self, base_config, debug):
        super(Sast, self).__init__(base_config, debug)

    def execute(self):
        self.print_info()
        sast_pipe_config = SastPipeConfig(self._base_config, self.debug)
        if self.debug:
            message = f'Debugging run_vars\n\n{sast_pipe_config.dump_configs()}'
            LOG.info(message)
        if sast_pipe_config.run_pipe:
            for run_config in sast_pipe_config.run_config:
                sast_module = getattr(
                    importlib.import_module(
                        f'picli.sast.{run_config.config[0]["sast"]}'
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
    config_file = context.obj.get('args')['config']
    debug = context.obj.get('args')['debug']
    sequence = base.get_sequence('sast')
    for action in sequence:
        base.execute_subcommand(config_file, action, debug)
