import abc
import os
import requests
import tempfile
import zipfile

from picli import logger
from picli import util

LOG = logger.get_logger(__name__)


class Base(object):
    """Base Lint object
    Defines the set of behaviours that all actions
    must share.

    All actions must have an execute method which will be
    called by PiCli's command module. The default implementation
    is found here and can be used by subclasses.

    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, pipe_config, run_config):
        self.pipe_config = pipe_config
        self.run_config = run_config
        self.run_vars = self._build_run_vars()

    def _build_run_vars(self):
        if self.options.get('options'):
            run_vars = util.merge_dicts(
                util.safe_load(self.pipe_config.dump_configs()),
                self.options
            )
        else:
            run_vars = util.safe_load(self.pipe_config.dump_configs())
        return run_vars

    @property
    @abc.abstractmethod
    def name(self):
        """
        Name of the action

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
        options = {
            'options': False
        }
        return options

    @abc.abstractmethod
    def execute(self):
        """
        Executes the action analyzer.

        This default implementation will zip all files in
        the configuration.files list and send that zipfile
        across the network to the specified SAST analyzer function.

        :return:  None
        """
        LOG.info(f"Executing: {self.name}")
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_file = self.zip_files(temp_dir)
            with open(zip_file.filename, 'rb') as file:
                files = [('files', file)]
                try:
                    if self.pipe_config.debug:
                        LOG.info(f'Sending zipfile to {self.url}')
                    r = requests.post(self.url, files=files)
                except requests.exceptions.RequestException as e:
                    message = f"Failed to execute {self.name}. \n\n{e}"
                    util.sysexit_with_message(message)
                try:
                    r.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    message = f'Failed to execute {self.name}. \n\n{e}'
                    util.sysexit_with_message(message)
                else:
                    LOG.warn(r.text)

    @property
    @abc.abstractmethod
    def url(self):
        """
        Defines the URL of the function which the execute method will hit
        :return: string
        """
        url_version = self.pipe_config.version.replace('.', '-')
        if self.pipe_config.version == 'latest':
            return f'{self.pipe_config.endpoint}/' \
                   f'piedpiper-{self.name}-function'
        else:
            return f'{self.pipe_config.endpoint}/' \
                   f'piedpiper-{self.name}-function-{url_version}'

    @abc.abstractmethod
    def zip_files(self, destination):
        """
        Zips all files in the run_config.files list if they match
        the SAST analyzer.
        :param destination: Path to create the zipfile in
        :return: ZipFile
        """
        zip_file = zipfile.ZipFile(
            f'{destination}/{self.name}.zip', 'w', zipfile.ZIP_DEFLATED
        )
        for file in self.run_config.files:
            if self.pipe_config.debug:
                message = f'Writing {file["file"]} to zip'
                LOG.info(message)
            zip_file.write(
                file['file'],
                os.path.relpath(file['file'], self.pipe_config.base_config.base_dir)
            )

        if self.pipe_config.debug:
            message = f'Writing run_vars.yml to zip.\n' \
                      f'run_vars.yml\n' \
                      f'{util.safe_dump(self.run_vars)}'
            LOG.info(message)
        zip_file.writestr("run_vars.yml", util.safe_dump(self.run_vars))

        zip_file.close()

        return zip_file

    @property
    def enabled(self):
        return self.run_config.run_pipe

    @property
    def options(self):
        """
        Merges default options with provided action configuration
        options.
        :return: dict
        """
        run_config_options = next(({'options': option['options']}
                                   for option in self.run_config.config
                                   if 'options' in option), None)
        if run_config_options:
            return util.merge_dicts(self.default_options,
                                    run_config_options)
        else:
            return self.default_options
