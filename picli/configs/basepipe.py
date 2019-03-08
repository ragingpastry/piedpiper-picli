import abc

from picli.config import BaseConfig
from picli import util


class PipeConfig(BaseConfig):
    __metaclass__ = abc.ABCMeta

    def __init__(self, base_config):
        super(PipeConfig, self).__init__(base_config)
        self._pipe_config = self._build_pipe_config()
        self._verify()

    def _build_pipe_config(self):
        with open(f'piedpiper.d/{self.vars_dir}/pipe_vars.d/pi_{self.name}.yml') as config:
            return util.safe_load(config)

    @property
    @abc.abstractmethod
    def name(self):
        pass

    @property
    def run_pipe(self):
        return self._pipe_config[f'pi_{self.name}_pipe_vars']['run_pipe']

    @property
    def endpoint(self):
        return self._pipe_config[f'pi_{self.name}_pipe_vars']['url']

    def _verify(self):
        pass
