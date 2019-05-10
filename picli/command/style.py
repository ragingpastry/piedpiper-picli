import click
from picli.command import base
from picli.config import BaseConfig
from picli.configs.style_pipe import StylePipeConfig
from picli import logger
from picli import util
import importlib

LOG = logger.get_logger(__name__)


class Style(base.Base):
    def __init__(self, config):
        super(Style, self).__init__(config)

    def execute(self):
        """
        Executes the style step.

        We will first initialize a StylePipeConfig object, passing in
        the 'pi_global_vars.yml' configuration file and a debug flag.
        We will then dynamically discover which styler we need to run
        based on the run_config of the StylePipeConfig object and then
        execute that styler.
        :return:
        """
        self.print_info()
        style_pipe_config = StylePipeConfig(self._base_config, self.debug)
        if style_pipe_config.run_pipe:
            for run_config in style_pipe_config.run_config:
                style_module = getattr(
                    importlib.import_module(
                        f'picli.actions.styler.{run_config.config[0]["styler"]}'
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
    debug = context.obj.get('args')['debug']
    config = BaseConfig(context.obj.get('args')['config'], debug)
    sequence = base.get_sequence('style')
    base.execute_sequence(sequence, config)
