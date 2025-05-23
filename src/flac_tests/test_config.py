import os
from pathlib import Path
from unittest import mock

import pytest

from flac import config
from flac.app import FlacApp


data_dpath = Path(__file__).parent / 'data'


@pytest.fixture
def app():
    return FlacApp.create('confapp', '/some/fake/dir', testing=True)


class TestConfig:
    def test_app_config_files(self, app):
        with mock.patch.dict(os.environ, {'HOME': '~'}):
            fpaths = config.app_config_fpaths(app, {})
            assert fpaths == [
                Path('/etc/confapp/config.py'),
                Path('~/.config/confapp/config.py'),
                Path(app.root_path.parent.resolve(), 'confapp-config.py'),
            ]

    def test_load_fpath_config(self, app):
        config_fpath = data_dpath / 'config.py'
        assert config.load_fpath_config(app, {}, config_fpath, 'foo') == {
            'default': 1,
            'foo': 2,
        }

    def test_load_config_fpaths(self, app):
        fpaths = [data_dpath / 'config.py', data_dpath / 'config2.py', '/not/there']
        result = config.load_fpath_configs(app, {}, fpaths, 'foo')
        assert result == {
            'default': 3,
            'foo': 2,
            'foo2': 4,
        }

    def test_environ_config(self):
        with mock.patch.dict(os.environ, {'FOO_BAR': 'baz'}):
            assert config.environ_config('foo') == {
                'BAR': 'baz',
            }

    def test_config_applied(self):
        with mock.patch.dict(config.os.environ, {'CONFAPP_BAR': 'baz'}):
            app = FlacApp.create('confapp', '/some/fake/dir', testing=True)
            assert app.config['BAR'] == 'baz'

    def test_no_profile_error(self):
        with pytest.raises(ValueError) as exc_ctx:
            FlacApp.create('confapp', '/some/fake/dir')
        assert (
            str(exc_ctx.value)
            == 'The configuration profile must be set with CONFAPP_CONFIG_PROFILE or the'
            ' --config-profile CLI option when app.testing and app.debug are both False.'
        )
