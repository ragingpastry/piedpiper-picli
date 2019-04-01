import click
from picli.command import base
from picli.configs.style_pipe import StylePipeConfig
from picli import logger
from picli import util
import importlib

LOG = logger.get_logger(__name__)


class Style(base.Base):
    def __init__(self, base_config, debug):
        super(Style, self).__init__(base_config, debug)

    def execute(self):
        self.print_info()
        style_pipe_config = StylePipeConfig(self._base_config, self.debug)
        if self.debug:
            message = f'Debugging run_vars\n\n{style_pipe_config.dump_configs()}'
            LOG.info(message)
        if style_pipe_config.run_pipe:
            for run_config in style_pipe_config.run_config:
                style_module = getattr(
                    importlib.import_module(
                        f'picli.styler.{run_config.config[0]["styler"]}'
                    ),
                    f'{util.camelize(run_config.config[0]["styler"])}'
                )
                styler = style_module(style_pipe_config, run_config)
                styler.execute()
        else:
            LOG.warn("Style step not enabled.\n\nSkipping...")


@click.command()
@click.pass_context
def style(context):
    config_file = context.obj.get('args')['config']
    debug = context.obj.get('args')['debug']
    sequence = base.get_sequence('style')
    for action in sequence:
        base.execute_subcommand(config_file, action, debug)
