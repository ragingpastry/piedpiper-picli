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
        if self.debug:
            message = f'Debugging run_vars\n\n{style_pipe_config.dump_configs()}'
            LOG.info(message)
        if style_pipe_config.run_pipe:
            stylers = set()
            for file in style_pipe_config.run_config.files:
                stylers.add(file['styler'])
            for styler in sorted(stylers):
                style_module = getattr(
                    importlib.import_module(
                        f'picli.styler.{styler}'
                    ),
                    f'{util.camelize(styler)}'
                )
                styler = style_module(style_pipe_config, style_pipe_config.run_config)
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
