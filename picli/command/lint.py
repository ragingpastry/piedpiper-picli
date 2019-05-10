import click
from picli.command import base
from picli.config import BaseConfig
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
    debug = context.obj.get('args')['debug']
    config = BaseConfig(context.obj.get('args')['config'], debug)
    sequence = base.get_sequence('lint')
    base.execute_sequence(sequence, config)

