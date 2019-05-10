import abc
import json
import os
import requests
import tempfile
import time
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
        self.run_id = self.pipe_config.base_config.run_id

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
        task_id = util.request_new_task_id(
            run_id=self.run_id,
            gman_url=self.pipe_config.base_config.gman_url,
            project=self.pipe_config.base_config.global_vars['project_name'],
        )

        if self.pipe_config.debug:
            LOG.info(f'Received taskID: {task_id}')

        with tempfile.TemporaryDirectory() as tempdir:
            artifact_file = self.zip_files(tempdir).filename
            artifact = {
                'file': artifact_file,
                'hashsum': util.generate_hashsum(artifact_file),
            }

            self.upload_artifacts([artifact])

        task_data = {
            'run_id': self.run_id,
            'project': self.pipe_config.base_config.global_vars['project_name'],
            'artifacts': [artifact],
        }

        headers = {
            'Content-Type': 'application/json'
        }

        try:
            if self.pipe_config.debug:
                LOG.info(f'Calling {self.name} gateway to {self.url}')
            r = requests.post(self.url, data=json.dumps(task_data), headers=headers)
        except requests.exceptions.RequestException as e:
            message = f'Failed to call {self.name} gateway. \n\n{e}'
            util.sysexit_with_message(message)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            message = f'Failed to call {self.name} gateway. \n\n{e}'
            self.pipe_config.base_config.update_state({
                self.name: {
                    'state': 'failed'
                }
            })
            util.sysexit_with_message(message)
        else:
            results = r.json()
            LOG.info(f"{self.name} function is executing with "
                     f"task_id {results.get('task_id')} and run_id {self.run_id}"
                     )
            util.wait_for_task_status(
                task_id=results.get('task_id'),
                status='completed',
                gman_url=self.pipe_config.base_config.gman_url,
                retry_max=20,
            )
            self.pipe_config.base_config.update_state({
                self.name: {
                    'state': 'completed'
                }
            })
            if self.pipe_config.debug:
                LOG.info(util.safe_dump(self.pipe_config.base_config.read_state()))

            self.display()

    def display(self):
        """
        Displays the log artifact generated from the PiedPiper FaaS
        :return: None
        """
        with tempfile.TemporaryDirectory() as tempdir:
            util.download_artifact(
                self.run_id,
                f'artifacts/{self.name}.log',
                f'{tempdir}/{self.name}.log',
                self.pipe_config.base_config.storage['url'],
                self.pipe_config.base_config.storage['access_key'],
                self.pipe_config.base_config.storage['secret_key']
            )
            with open(f'{tempdir}/{self.name}.log') as results:
                LOG.out(results.read())

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
                   f'piedpiper-{self.name}-gateway'
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

    def upload_artifacts(self, artifacts):
        """
        Uploads a list of artifacts to the defined storage after checking in with Artman
        to ensure that the files aren't already uploaded.

        :param artifacts: List of artifact dictionaries to upload
        :return:
        """
        for artifact in artifacts:
            artifact_uri = util.get_artifact_uri(
                hash=artifact['hashsum'],
                gman_url=self.pipe_config.base_config.gman_url
            )

            if not artifact_uri:
                if self.pipe_config.debug:
                    LOG.info(f"Artifact not found. Uploading to bucket {self.run_id}")
                artifact_object = util.upload_artifact(
                    self.run_id,
                    f"artifacts/{os.path.basename(artifact['file'])}",
                    artifact['file'],
                    self.pipe_config.base_config.storage.get('url'),
                    self.pipe_config.base_config.storage.get('access_key'),
                    self.pipe_config.base_config.storage.get('secret_key'),
                )
                print(artifact_object)
                action_state = {
                    self.name: {
                        'state': 'uploaded',
                        'artifact_uri': f'{self.run_id}/{self.name}.zip',
                        'etag': artifact_object.etag,
                        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', artifact_object.last_modified)
                    }
                }
            else:
                action_state = {
                    self.name: {
                        'state': 'found',
                        'artifact_uri': artifact_uri.get('uri'),
                        'etag': None
                    }
                }

            if self.pipe_config.debug:
                LOG.info(util.safe_dump(action_state))
            self.pipe_config.base_config.update_state(action_state)

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
