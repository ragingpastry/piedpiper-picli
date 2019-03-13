from picli.model import base_schema
from picli import logger
from picli import util

LOG = logger.get_logger(__name__)


class BaseConfig(object):

    def __init__(self, config):
        self._base_path = util.find_piedpiper_dir(config)
        self._config = self._read_config(config)
        self._validate()

    def _read_config(self, config):
        try:
            with open(config) as c:
                return util.safe_load(c)
        except IOError as e:
            message = f"Failed to parse config. \n\n{e}"
            util.sysexit_with_message(message)

    def _validate(self):
        errors = base_schema.validate(self._config)
        if errors:
            msg = f"Failed to validate. \n\n{errors.messages}"
            util.sysexit_with_message(msg)

    @property
    def vars_dir(self):
        return self._base_path + '/' + 'piedpiper.d/' + self._config['pi_global_vars']['vars_dir']

    @property
    def piedpiper_dir(self):
        return self._base_path


    @property
    def ci_provider(self):
        return self._config['pi_global_vars']['ci_provider']

    @property
    def ci_provider_file(self):
        if self._config['pi_global_vars']['ci_provider'] == 'gitlab-ci':
            return '.gitlab-ci.yml'

    @property
    def version(self):
        return self._config['version']

