import os

from appdirs import user_config_dir
from tomlkit import parse


class Configuration(object):
    DEFAULT_CONFIG_PATH = os.path.join(user_config_dir('adr'), 'config.toml')
    DEFAULTS = {
        "debug": False,
        "debug_url": "https://activedata.allizom.org/tools/query.html#query_id={}",
        "fmt": "table",
        "url": "https://activedata.allizom.org/query",
        "verbose": False,
    }

    def __init__(self, path=None):
        self.path = path or self.DEFAULT_CONFIG_PATH

        self._config = self.DEFAULTS.copy()
        if os.path.isfile(self.path):
            with open(self.path, 'r') as fh:
                content = fh.read()
                self.update(parse(content)['adr'])

    def __getitem__(self, key):
        return self._config[key]

    def __getattr__(self, key):
        return self[key]

    def update(self, data):
        """
        :param dict config: dictionary object of config
        """
        self._config.update(data)
