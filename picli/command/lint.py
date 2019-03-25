import click
from picli.command import base
from picli.configs.lint_pipe import LintPipeConfig
from picli import logger
from picli import util
import importlib

LOG = logger.get_logger(__name__)


class Lint(base.Base):
    def __init__(self, base_config, debug):
        super(Lint, self).__init__(base_config, debug)

    def execute(self):
        self.print_info()
        lint_pipe_config = LintPipeConfig(self._base_config, self.debug)
        if self.debug:
            message = f'Debugging run_vars\n\n{lint_pipe_config.dump_configs()}'
            LOG.info(message)
        if lint_pipe_config.run_pipe:
            linters = set()
            for file in lint_pipe_config.run_config.files:
                linters.add(file['linter'])
            for linter in sorted(linters):
                linter_module = getattr(
                    importlib.import_module(
                        f'picli.linter.{linter}'
                    ),
                    f'{util.camelize(linter)}'
                )
                linter = linter_module(lint_pipe_config, lint_pipe_config.run_config)
                linter.execute()
        else:
            LOG.warn("Lint step not enabled.\n\nSkipping...")


@click.command()
@click.pass_context
def lint(context):
    config_file = context.obj.get('args')['config']
    debug = context.obj.get('args')['debug']
    sequence = base.get_sequence('lint')
    for action in sequence:
        base.execute_subcommand(config_file, action, debug)
