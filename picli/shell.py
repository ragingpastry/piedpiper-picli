import click

from picli import command


@click.group()
@click.option(
    '--config',
    '-c',
    default='piedpiper.d/pi_global_vars.yml',
    help='The PiCli configuration file to use'
)
@click.option(
    '--debug',
    is_flag=True,
    default=False,
    help='Enable debug logging'
)
@click.pass_context
def main(context, config, debug):
    context.obj = {}
    context.obj['args'] = {}
    context.obj['args']['config'] = config
    context.obj['args']['debug'] = debug


main.add_command(command.lint.lint)
main.add_command(command.style.style)
main.add_command(command.sast.sast)
main.add_command(command.validate.validate)
main.add_command(command.unit.unit)
