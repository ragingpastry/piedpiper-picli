import tempfile
import time
import logging
import requests
import json
import zipfile

from picli.actions import base
from picli import logger
from picli import util

LOG = logger.get_logger(__name__)


class Validator(base.Base):
    """Validation object to perform checks against a PiCli run.

    Creates a zip of the configuration files supplied by
    the base_config object provided during initialization. This config
    is written to a run_vars.yml file which is sent to an external validation
    function.
    We then parse the results of the validation. If the policy checks are
    set to enforcing then we will exit, if they are set to permissive then we
    will warn the user and continue with the execution.

    """
    def __init__(self, pipe_config):
        """
        Initialize the Validator.
        :param base_config: ValidatePipeConfig object
        """
        self.pipe_config = pipe_config
        self.run_id = self.pipe_config.base_config.run_id

    @property
    def name(self):
        return 'validator'

    @property
    def url(self):
        return super().url

    def zip_files(self, destination):
        """
        Create a zipfile containing run variables of PiCli.
        :param destination: Directory to write zipfile to
        :return: ZipFile
        """
        try:
            zip_file = zipfile.ZipFile(
                f'{destination}/validation.zip', 'w', zipfile.ZIP_DEFLATED
            )
            if self.pipe_config.debug:
                message = f'Writing run_vars.yml to zip'
                LOG.info(message)
            zip_file.writestr("run_vars.yml", self.pipe_config.dump_configs())
            zip_file.close()
            return zip_file
        except Exception as e:
            message = f"Zipping failed in validator. \n\n{e}"
            util.sysexit_with_message(message)

    """
    Questions: 
    Execute will:
      1. Request a new taskID from Gman and a new runID if one was not provided
      2. Hash our zipfiles and send the file hash to artman along with the task ID
      2a. If the file hash is found then artman will respond with a 302 found? and the URI
      2a.1 If 302 found and we receive a URI then we record this in a state file
      2a.2 If not then artman will respond with a 404 not found. We will then upload files to minio
           and receive a file URI from minio. This will be recorded in the state file. We
           then go back and tell artman that we uploaded a file at a specific URI and give it the task ID and hash
      3. Now we call the validate function with the code URI, vars URI, and run ID. Validate faas responds with a task ID
         which it got from gman.
      4. We then poll gman with the given validate faas task ID until the task ID state is errored or completed.
    """
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
            hashsum = util.generate_hashsum(artifact_file)

            self.upload_artifacts([artifact_file], hashsum)

        task_data = {
            'run_id': self.run_id,
            'project': self.pipe_config.base_config.global_vars['project_name'],
            'hashsum': hashsum,
        }

        headers = {
            'Content-Type': 'application/json'
        }

        try:
            if self.pipe_config.debug:
                LOG.info(f'Calling validator gateway to {self.url}')
            r = requests.post(self.url, data=json.dumps(task_data), headers=headers)
        except requests.exceptions.RequestException as e:
            message = f'Failed to call validator gateway validator. \n\n{e}'
            util.sysexit_with_message(message)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            message = f'Failed to call validator gateway validator. \n\n{e}'
            self.pipe_config.base_config.update_state({
                'validate': {
                    'state': 'failed'
                }
            })
            util.sysexit_with_message(message)
        else:
            results = r.json()['result']
            LOG.info(f"Validation function is executing with "
                     f"task_id {results.get('task_id')} and run_id {self.run_id}"
                     )
            util.wait_for_task_status(
                task_id=results.get('task_id'),
                status='completed',
                gman_url=self.pipe_config.base_config.gman_url,
                retry_max=20,
            )
            self.pipe_config.base_config.update_state({
                'validate': {
                    'state': 'completed'
                }
            })
            with tempfile.TemporaryDirectory() as tempdir:
                util.download_artifact(
                    self.run_id,
                    'artifacts/validation.log',
                    f'{tempdir}/validation.log',
                    self.pipe_config.base_config.storage['url'],
                    self.pipe_config.base_config.storage['access_key'],
                    self.pipe_config.base_config.storage['secret_key']
                )
                with open(f'{tempdir}/validation.log') as results:
                    self._parse_results(util.safe_load(results))

    def _parse_results(self, results):
        """
        Parse results returned from the execute request.
        Builds a list of errors found in the JSON-object
        and

        :param results: JSON-object from execute
        :return: None
        """
        result_list = []
        for stage_result in results:
            for value in stage_result.values():
                if value['errors']:
                    result_list.append(stage_result)
        if len(result_list):
            if self.pipe_config.policy_enforcing:
                util.sysexit_with_message(
                    json.dumps(result_list, indent=4)
                )
            else:
                LOG.warn(json.dumps(result_list, indent=4))
        LOG.success("Validation completed successfully.")

    def _is_deduplicated(self, input_file):
        file_hash = util.generate_hashsum(input_file)

        try:
            if self.config.debug:
                LOG.info(f'Sending hash of {input_file} to {self.url}')
            r = requests.get(f"{self.config.base_config.gman_url}/hash/{file_hash}")
        except requests.exceptions.RequestException as e:
            message = f'Failed to send hash to {self.config.base_config.gman_url}. \n\n{e}'
            util.sysexit_with_message(message)
        else:
            if r.status_code == 302:
                if self.config.debug:
                    LOG.info(f'Hashsum found')
                return r.json()
            elif r.status_code == 404:
                if self.config.debug:
                    LOG.info('Hashsum not found')
                return False
