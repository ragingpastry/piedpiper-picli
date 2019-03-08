from picli import util


class BaseConfig(object):

    def __init__(self, config):
        self._config = self._read_config(config)

    def _read_config(self, config):
        with open(config) as c:
            return util.safe_load(c)

    @property
    def vars_dir(self):
        return self._config['pi_global_vars']['vars_dir']

