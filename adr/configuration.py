import os
from pathlib import Path

from appdirs import user_config_dir
from cachy import CacheManager
from cachy.stores import NullStore
from tomlkit import parse

import adr


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
    DEFAULT_CONFIG_PATH = Path(user_config_dir('adr')) / 'config.toml'
    DEFAULTS = {
        "cache": None,
        "debug": False,
        "debug_url": "https://activedata.allizom.org/tools/query.html#query_id={}",
        "fmt": "table",
        "sources": [os.getcwd(), Path(adr.__file__).parent.parent],
        "url": "https://activedata.allizom.org/query",
        "verbose": False,
    }

    def __init__(self, path=None):
        self.path = Path(path or os.environ.get('ADR_CONFIG_PATH') or self.DEFAULT_CONFIG_PATH)

        self._config = self.DEFAULTS.copy()
        if self.path.is_file():
            with open(self.path, 'r') as fh:
                content = fh.read()
                self.merge(parse(content)['adr'])

        # Use the NullStore by default. This allows us to control whether
        # caching is enabled or not at runtime.
        cache = self._config['cache'] or {'stores': {'null': {'driver': 'null'}}}
        self.cache = CacheManager(cache)
        self.cache.extend('null', lambda driver: NullStore())

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


config = Configuration()
