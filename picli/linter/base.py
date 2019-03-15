import abc
import requests
import tempfile
import zipfile

from picli import logger
from picli import util

LOG = logger.get_logger(__name__)


class Base(object):
    """Base Lint object
    Defines the set of behaviours that all linters
    must share.

    All linters must have an execute method which will be
    called by PiCli's command module. The default implementation
    is found here and can be used by subclasses.

    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, base_config, config):
        self.config = base_config
        self.run_config = config

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
        Executes the linter.

        This default implementation will zip all files in
        the configuration.files list and send that zipfile
        across the network to the specified linter function.

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
        """
        Defines the URL of the function which the execute method will hit
        :return: string
        """
        return self.config.endpoint + f'/piedpiper-{self.name}-function'

    @abc.abstractmethod
    def zip_files(self, destination):
        """
        Zips all files in the run_config.files list if they match
        the linter.
        :param destination: Path to create the zipfile in
        :return: ZipFile
        """
        zip_file = zipfile.ZipFile(
            f'{destination}/{self.name}.zip', 'w', zipfile.ZIP_DEFLATED
        )
        for file in self.run_config.files:
            if file['linter'] == f'{self.name}':
                zip_file.write(
                    f"{self.config.base_config.base_dir}/{file['file']}",
                    file['file']
                )
        zip_file.close()

        return zip_file

    @property
    def enabled(self):
        return self.run_config.run_pipe

    @property
    def options(self):
        """
        Merges default options with provided linter configuration
        options.
        FIXME: Not currently used.

        :return: dict
        """
        return util.merge_dicts(self.default_options,
                                self.run_config.config['linter']['options'])
