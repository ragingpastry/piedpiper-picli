import click
from picli.command import base
from picli.config import BaseConfig
from picli.configs.validate_pipe import ValidatePipeConfig
from picli import logger
from picli.actions.validators.validator import Validator

LOG = logger.get_logger(__name__)


class Validate(base.Base):

    def execute(self):
        self.print_info()
        validator_config = ValidatePipeConfig(self.base_config)
        if self.base_config.debug:
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
    debug = context.obj.get('args')['debug']
    config = BaseConfig(context.obj.get('args')['config'], debug)
    sequence = base.get_sequence('validate')
    base.execute_sequence(sequence, config)
