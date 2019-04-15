import click
from picli.command import base
from picli import logger

LOG = logger.get_logger(__name__)


@click.command()
@click.pass_context
def lint(context):
    """
    Command used to execute the "lint" container found in
    command.base
    :param context:
    :return: None
    """
    config_file = context.obj.get('args')['config']
    debug = context.obj.get('args')['debug']
    sequence = base.get_sequence('lint')
    for action in sequence:
        base.execute_subcommand(config_file, action, debug)
