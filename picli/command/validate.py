import click
from picli.command import base
from picli.configs.validate_pipe import ValidatePipeConfig
from picli import logger
from picli.validators.validator import Validator

LOG = logger.get_logger(__name__)


class Validate(base.Base):

    def execute(self):
        self.print_info()
        validator_config = ValidatePipeConfig(self._base_config, self.debug)
        if self.debug:
            message = f'Debugging run_vars\n\n{validator_config.dump_configs()}'
            LOG.info(message)
        if validator_config.run_pipe:
            validator = Validator(validator_config)
            validator.execute()
        else:
            LOG.warn("Validate step not enabled.\n\nSkipping...")


@click.command()
@click.pass_context
def validate(context):
    config_file = context.obj.get('args')['config']
    debug = context.obj.get('args')['debug']
    sequence = base.get_sequence('validate')
    for action in sequence:
        base.execute_subcommand(config_file, action, debug)
