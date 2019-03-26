import tempfile
import requests
import json
import zipfile

from picli import logger
from picli import util

LOG = logger.get_logger(__name__)


class Validator(object):
    """Validation object to perform checks against a PiCli run.

    Creates a zip of the configuration files supplied by
    the base_config object provided during initialization. This config
    is written to a run_vars.yml file which is sent to an external validation
    function.
    We then parse the results of the validation. If the policy checks are
    set to enforcing then we will exit, if they are set to permissive then we
    will warn the user and continue with the execution.

    """
    def __init__(self, base_config):
        """
        Initialize the Validator.
        :param base_config: ValidatePipeConfig object
        """
        self.config = base_config

    @property
    def name(self):
        return 'validator'

    @property
    def url(self):
        url_version_string = self.config.version.replace('.', '-')
        if self.config.version == 'latest':
            return f'{self.config.endpoint}/piedpiper-{self.name}-function'
        else:
            return f'{self.config.endpoint}/piedpiper-{self.name}-function-{url_version_string}'

    @property
    def enabled(self):
        return self.config.run_pipe

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
            if self.config.debug:
                message = f'Writing run_vars.yml to zip'
                LOG.info(message)
            zip_file.writestr("run_vars.yml", self.config.dump_configs())
            zip_file.close()
            return zip_file
        except Exception as e:
            message = f"Zipping failed in validator. \n\n{e}"
            util.sysexit_with_message(message)

    def execute(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_file = self.zip_files(temp_dir)
            files = [('files', open(zip_file.filename, 'rb'))]
            try:
                if self.config.debug:
                    LOG.info(f'Sending zipfile to {self.url}')
                r = requests.post(self.url, files=files)
            except requests.exceptions.RequestException:
                message = f'Failed to execute validator. \n\n{e}'
                util.sysexit_with_message(message)
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                message = f'Failed to execute validator. \n\n{e}'
                util.sysexit_with_message(message)
            else:
                results = r.json()
                self._parse_results(results)

    def _parse_results(self, results):
        """
        Parse results returned from the execute request.
        Builds a list of errors found in the JSON-object
        and

        :param results: JSON-object from execute
        :return: None
        """
        result_list = []
        for result in results.values():
            for stage_result in result:
                for value in stage_result.values():
                    if value['errors']:
                        result_list.append(stage_result)
        if len(result_list):
            if self.config.policy_enforcing:
                util.sysexit_with_message(
                    json.dumps(result_list, indent=4)
                )
            else:
                LOG.warn(json.dumps(result_list, indent=4))
        LOG.success("Validation completed successfully.")
