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

        cfg = self.DEFAULTS.copy()
        if os.path.isfile(self.path):
            with open(self.path, 'r') as fh:
                content = fh.read()
                cfg.update(parse(content)['adr'])

        self.update(cfg)

    def update(self, config):
        """
        :param dict config: dictionary object of config
        """
        for key, value in config.items():
            setattr(self, key, value)
