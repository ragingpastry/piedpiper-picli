import click
from picli.command import base
from picli.configs.unit_pipe import UnitPipeConfig
from picli import logger
from picli import util
import importlib

LOG = logger.get_logger(__name__)


class Unit(base.Base):
    def __init__(self, base_config, debug):
        super(Unit, self).__init__(base_config, debug)

    def execute(self):
        self.print_info()
        unit_pipe_config = UnitPipeConfig(self._base_config, self.debug)
        if unit_pipe_config.run_pipe:
            for run_config in unit_pipe_config.run_config:
                unit_tester_module = getattr(
                    importlib.import_module(
                        f'picli.unit.{run_config.config[0]["unit"]}'
                    ),
                    f'{util.camelize(run_config.config[0]["unit"])}'
                )
                unit_tester = unit_tester_module(unit_pipe_config, run_config)
                if self.debug:
                    message = f'Debugging run_vars\n\n{util.safe_dump(unit_tester.run_vars)}'
                    LOG.info(message)
                unit_tester.execute()
        else:
            LOG.warn("Unit step not enabled.\n\nSkipping...")


@click.command()
@click.pass_context
def unit(context):
    config_file = context.obj.get('args')['config']
    debug = context.obj.get('args')['debug']
    sequence = base.get_sequence('unit')
    for action in sequence:
        base.execute_subcommand(config_file, action, debug)
