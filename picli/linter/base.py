import os
import abc

from picli import util


class Base(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, base_config, config):
        self._base_config = base_config
        self._config = config

    @property
    @abc.abstractmethod
    def name(self):
        """
        Name of the linter

        :return: str
        """
        pass

    @property
    @abc.abstractmethod
    def default_options(self):
        """
        Default CLI arguments provided to command

        :return: dict
        """
        pass

    @abc.abstractmethod
    def execute(self):
        """
        Executes command

        :return:  None
        """
        pass

    @property
    @abc.abstractmethod
    def url(self):
        pass

    @property
    def enabled(self):
        return self._config.config['linter']['enabled']

    @property
    def options(self):
        return util.merge_dicts(self.default_options, self._config.config['linter']['options'])

