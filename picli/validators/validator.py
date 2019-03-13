import tempfile
import requests
import json
import zipfile

from picli import logger
from picli import util

LOG = logger.get_logger(__name__)


class Validator(object):
    def __init__(self, base_config):
        self._base_config = base_config

    @property
    def name(self):
        return 'validator'

    @property
    def url(self):
        return self._base_config.endpoint + f'/piedpiper-{self.name}-function'

    @property
    def enabled(self):
        return self._base_config.run_pipe

    def zip_files(self, destination):
        try:
            zip_file = zipfile.ZipFile(f'{destination}/validation.zip', 'w', zipfile.ZIP_DEFLATED)
            zip_file.writestr("run_vars.yml", self._base_config.dump_configs())
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
                r = requests.post(self.url, files=files)
                results = r.json()
                result_list = []
                for result in results.values():
                    for stage_result in result:
                        for value in stage_result.values():
                            if value == True:
                                continue
                            else:
                                result_list.append(stage_result)
                if len(result_list):
                    if self._base_config.policy_checks_enforcing:
                        util.sysexit_with_message(
                            json.dumps(result_list, indent=4)
                        )
                    else:
                        LOG.warn(json.dumps(result_list, indent=4))
                LOG.success("Validation completed successfully.")
            except requests.exceptions.RequestException as e:
                message = f"Failed to execute validator. \n\n{e}"
                util.sysexit_with_message(message)

