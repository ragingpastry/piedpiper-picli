import abc
import requests
import tempfile
import zipfile

from picli import logger
from picli import util

LOG = logger.get_logger(__name__)


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
        LOG.info(f"Executing linter {self.name}")
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_file = self.zip_files(temp_dir)
            files = [('files', open(zip_file.filename, 'rb'))]
            try:
                r = requests.post(self.url, files=files)
                LOG.warn(r.text)
            except requests.exceptions.RequestException as e:
                message = f"Failed to execute linter {self.name}. \n\n{e}"
                util.sysexit_with_message(message)

    @property
    @abc.abstractmethod
    def url(self):
        return self._base_config.endpoint + f'/piedpiper-{self.name}-function'

    @abc.abstractmethod
    def zip_files(self, destination):
        zip_file = zipfile.ZipFile(f'{destination}/{self.name}.zip', 'w', zipfile.ZIP_DEFLATED)
        for file in self._config.files:
            if file['linter'] == f'{self.name}':
                zip_file.write(f"{self._base_config._base_config.piedpiper_dir}/{file['file']}", file['file'])
        zip_file.close()

        return zip_file

    @property
    def enabled(self):
        return self._config.run_pipe

    @property
    def options(self):
        return util.merge_dicts(self.default_options, self._config.config['linter']['options'])

