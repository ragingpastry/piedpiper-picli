import tempfile
import requests
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
                LOG.warn(r.text)
            except requests.exceptions.RequestException as e:
                message = f"Failed to execute validator. \n\n{e}"
                util.sysexit_with_message(message)

