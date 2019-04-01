import os

from picli.model import base_schema
from picli import logger
from picli import util

LOG = logger.get_logger(__name__)


class BaseConfig(object):

    def __init__(self, config, debug):
        self.base_path = self._find_base_dir(config)
        self.config = self._read_config(config)
        self.debug = debug
        self._validate()

    def _find_base_dir(self, config):
        """

        :param config: pi_global_vars configuration file
        :return: Directory that is two levels up from
        configuration file. This will be the base directory
        that all other methods will assume.
        """
        #base_dir = os.path.dirname(os.path.dirname(config))
        base_dir = os.path.basename(os.path.normpath(os.path.join(os.path.abspath(config), '../..')))
        if not base_dir:
            base_dir = '.'
        return base_dir

    def _read_config(self, config):
        """
        Read pi_global_vars configuration file
        and return a YAML object.
        :param config: Path to configuration file
        :return: YAML object
        """
        try:
            with open(config) as c:
                return util.safe_load(c)
        except IOError as e:
            message = f"Failed to parse config. \n\n{e}"
            util.sysexit_with_message(message)

    def _validate(self):
        """
        Validate the loaded configuration object.
        Validations are defined in model/base_schema.py
        :return: None. Exit if errors are found.
        """
        errors = base_schema.validate(self.config)
        if errors:
            msg = f"Failed to validate. \n\n{errors.messages}"
            util.sysexit_with_message(msg)

    @property
    def global_vars(self):
        """
        Property defining the pi_global_vars dict.
        :return: pi_global_vars dict
        """
        return self.config['pi_global_vars']

    @property
    def vars_dir(self):
        """
        Property defining the vars_directory to use.
        By default this will be {base_dir}/piedpiper.d/default_vars.d
        :return:
        """

        if os.path.isdir(self.piedpiper_dir + self.global_vars['vars_dir']):
            return self.piedpiper_dir + self.global_vars['vars_dir']
        else:
            message = f"Piedpiper vars directory doesn't exist in {self.piedpiper_dir}." \
                      f"You gave {self.global_vars['vars_dir']}."
            util.sysexit_with_message(message)

    @property
    def base_dir(self):
        return self.base_path

    @property
    def piedpiper_dir(self):
        """
        Property defining the location of the pipedpiper.d directory.

        :return: String of path to piedpiper.d directory.
        """
        piedpiper_dir = 'piedpiper.d/'
        if os.path.isdir(piedpiper_dir):
            return piedpiper_dir
        else:
            message = f"Piedpiper directory doesn't exist in {piedpiper_dir}."
            util.sysexit_with_message(message)

    @property
    def ci_provider(self):
        """
        Property defining the ci_provider dict inside of global_vars.
        :return:
        """
        return self.global_vars['ci_provider']

    @property
    def ci_provider_file(self):
        """
        Property defining the name and location of the
        CI provider configuration file. Currently we only
        support gitlab.
        :return: .gitlab-ci.yml
        """
        if self.global_vars['ci_provider'] == 'gitlab-ci':
            return '.gitlab-ci.yml'

    @property
    def version(self):
        return self.global_vars['version']
