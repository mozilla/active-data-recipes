import os
from copy import deepcopy

import pytest
from appdirs import user_config_dir
from tomlkit import dumps

from adr.util.config import (
    Configuration,
    merge_to,
)


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

    config = create_config({'sources': ['foo']})
    config.merge({'sources': ['bar']})
    assert set(config.sources) == set(['foo', 'bar'])

    config.update({'sources': ['baz']})
    assert config['sources'] == ['baz']


def test_merge_to():
    a = {'l': [1], 'd': {'one': 1}}
    b = {'l': 1, 'd': 1}
    assert merge_to(a, deepcopy(b)) == {'d': {'one': 1}, 'l': [1]}
    assert merge_to(b, deepcopy(a)) == {'d': 1, 'l': 1}

    a = {'one': 1, 'l1': [1], 'l2': [1, 2], 'd1': {'d2': {'foo': 'bar'}}, 'd3': None}
    b = {'one': 2, 'two': 2, 'l1': False, 'l2': [3, 4], 'd1': {'d2': {'baz': True}}, 'd3': {}}
    assert merge_to(a, deepcopy(b)) == {
        'one': 1,
        'two': 2,
        'l1': [1],
        'l2': [3, 4, 1, 2],
        'd1': {'d2': {'foo': 'bar', 'baz': True}},
        'd3': None,
    }
    assert merge_to(b, deepcopy(a)) == {
        'one': 2,
        'two': 2,
        'l1': False,
        'l2': [1, 2, 3, 4],
        'd1': {'d2': {'foo': 'bar', 'baz': True}},
        'd3': {},
    }
