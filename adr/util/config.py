import os

from appdirs import user_config_dir
from tomlkit import parse


def merge_to(source, dest):
    """
    Merge dict and arrays (override scalar values).

    Keys from source override keys from dest, and elements from lists in source
    are appended to lists in dest.

    Args:
        source (dict): to copy from
        dest (dict): to copy to (modified in place)
    """
    for key, value in source.items():

        if key not in dest:
            dest[key] = value
            continue

        # Merge dict
        if isinstance(value, dict) and isinstance(dest[key], dict):
            merge_to(value, dest[key])
            continue

        if isinstance(value, list) and isinstance(dest[key], list):
            dest[key] = dest[key] + value
            continue

        dest[key] = value

    return dest


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
                self.merge(parse(content)['adr'])

    def __getitem__(self, key):
        return self._config[key]

    def __getattr__(self, key):
        return self[key]

    def merge(self, other):
        """Merge data into config (updates dicts and lists instead of
        overwriting them).

        Args:
            other (dict): Dictionary to merge configuration with.
        """
        merge_to(other, self._config)
