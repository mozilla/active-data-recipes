import os

import pytest
from appdirs import user_config_dir
from tomlkit import dumps

from adr.util.config import Configuration


@pytest.fixture
def create_config(tmpdir):

    def inner(data):

        config_path = tmpdir.join('config.toml')
        with open(config_path, 'w') as fh:
            fh.write(dumps({'adr': data}))
        return Configuration(config_path.strpath)

    return inner


def test_config(create_config):
    config = Configuration()
    assert config.path == os.path.join(user_config_dir('adr'), 'config.toml')

    config = create_config({})
    assert config['verbose'] is False
    assert config.debug is False
    assert config._config == Configuration.DEFAULTS

    config = create_config({'verbose': True})
    assert config.verbose is True
    assert config.debug is False
