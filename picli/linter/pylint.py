import requests
import zipfile

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
        return self._base_config._config['pylint']['url']

    def zip_files(self):
        zip_file = zipfile.ZipFile('flake8.zip', 'w', zipfile.ZIP_DEFLATED)
        for file in self._config.files:
            if file['linter'] == 'flake8':
                zip_file.write(file['file'])
        zip_file.close()

        return zip_file

    def execute(self):
        self.zip_files()
        files = [('files', open('flake8.zip', 'rb'))]
        try:
            r = requests.post(self.url, files=files)
            print(r.text)
        except requests.exceptions.RequestException as e:
            print(e)