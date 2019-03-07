import click
from picli.command import base
from picli.config import BaseConfig
from picli import util
import importlib


class Lint(base.Base):

    def execute(self):
        linters = set()
        for file in self._config.files:
            linters.add(file['linter'])

        for linter in linters:
            linter_module = getattr(importlib.import_module(f'picli.linter.{linter}'), f'{util.camelize(linter)}')
            linter = linter_module(self._base_config, self._config)
            linter.execute()


@click.command()
@click.pass_context
def lint(context):
    config_file = context.obj.get('args')['config']
    base_config = BaseConfig(config_file)
    for lint_config in base_config.lint_config:
        action = Lint(base_config, lint_config)
        action.execute()
