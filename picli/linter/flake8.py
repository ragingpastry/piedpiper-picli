import requests
import tempfile
import zipfile

from picli import util
from picli.linter import base


class Flake8(base.Base):

    def __init__(self, base_config, config):
        super(Flake8, self).__init__(base_config, config)

    @property
    def name(self):
        return 'flake8'

    @property
    def default_options(self):
        options = self._config.flake8_options

        return options

    @property
    def url(self):
        return self._base_config._config['flake8']['url']

    def zip_files(self, destination):
        zip_file = zipfile.ZipFile(f'{destination}/flake8.zip', 'w', zipfile.ZIP_DEFLATED)
        for file in self._config.files:
            if file['linter'] == 'flake8':
                zip_file.write(file['file'])
        zip_file.close()

        return zip_file

    def execute(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_file = self.zip_files(temp_dir)
            files = [('files', open(zip_file.filename, 'rb'))]
            try:
                r = requests.post(self.url, files=files)
                print(r.text)
            except requests.exceptions.RequestException as e:
                print(e)

