import picli.command
from picli import config
from picli import util
import os


class Base(object):
    def __init__(self, base_config, lint_config):
        self._config = lint_config
        self._base_config = base_config

