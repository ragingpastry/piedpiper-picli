import click

from picli import command


@click.group()
@click.option(
    '--config',
    '-c',
    default='piedpiper.d/pi_global_vars.yml',
    help='The PiCli configuration file to use'
)
@click.pass_context
def main(context, config):
    context.obj = {}
    context.obj['args'] = {}
    context.obj['args']['config'] = config


main.add_command(command.lint.lint)
main.add_command(command.validate.validate)
