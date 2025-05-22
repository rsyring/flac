import os
from pathlib import Path

import platformdirs

from . import app


def init_config(app: 'app.FlacApp', profile_name: str):
    app.config.update(build_config(app, profile_name))


def build_config(app: 'app.FlacApp', profile_name: str):
    env_config = environ_config(app.name)

    profile_name = env_config.pop('CONFIG_PROFILE', profile_name)
    if not profile_name and app.testing:
        profile_name = 'testing'
    elif not profile_name and app.debug:
        profile_name = 'development'

    if not profile_name:
        raise ValueError(
            f'The configuration profile must be set with {environ_key(app.name, "CONFIG_PROFILE")}'
            ' or the --config-profile CLI option when app.testing and app.debug are both False.',
        )

    # TODO: set default_config on the app and then call it as app.default_config so that
    # it can be easily overriden.
    config = default_config(app, profile_name) | env_config

    config_fpaths = app_config_fpaths(app, config)
    config = load_fpath_configs(app, config, config_fpaths, profile_name)
    config.update()

    config['_flac.config.fpaths'] = config_fpaths
    config['_flac.config.profile_name'] = profile_name

    return config


def load_fpath_configs(app, config, fpaths, config_prefix):
    for fpath in map(Path, fpaths):
        if not fpath.exists():
            continue
        config = load_fpath_config(app, config, fpath, config_prefix)

    return config


def load_fpath_config(app, config, fpath, config_prefix):
    pymod_vars = {'__file__': str(fpath)}
    exec(fpath.read_bytes(), pymod_vars)

    # Default config has at least two purposes:
    # 1) Set defaults at the OS/User level while still being able to override at the app config
    #    level.
    # 2) Enable a default config without knowing the prefix name.  Helpful in deployed environments
    #    where only a single config exists and will be used by default.
    config = call_env_config(app, config, pymod_vars, 'default')
    if config_prefix:
        config = call_env_config(app, config, pymod_vars, config_prefix)

    return config


def call_env_config(app, config, pymod_vars, config_prefix):
    callable_name = f'{config_prefix}_config'
    if callable_name in pymod_vars:
        return pymod_vars[callable_name](app, config)

    return config


def app_config_fpaths(app, config):
    config_fpaths = [
        # TODO: should work on Windows too
        Path(f'/etc/{app.name}/config.py'),
        Path(platformdirs.user_config_dir(app.name), 'config.py'),
        Path(app.root_path.parent.resolve(), f'{app.name}-config.py'),
    ]
    env_config_fpath = config.get('CONFIG_FILE')

    if env_config_fpath:
        config_fpaths.append(Path(env_config_fpath).resolve())

    return config_fpaths


def default_config(app, config_profile):
    return {
        # TODO: shouldn't be here?
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    }


def environ_key(app_name: str, key: str):
    return f'{app_name.upper()}_{key}'


def environ_config(app_name: str):
    retval = {}
    app_prefix = environ_key(app_name, '')
    for key, val in os.environ.items():
        if key.startswith(app_prefix):
            config_key = key.replace(app_prefix, '', 1)
            retval[config_key] = val

    return retval
