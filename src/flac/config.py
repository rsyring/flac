import os
import os.path as osp
import pathlib

import appdirs


def init_config(app, profile_name):
    app.config.update(build_config(app, profile_name))


def build_config(app, profile_name):
    env_config = environ_config(app)

    profile_name = env_config.pop("CONFIG_PROFILE", profile_name)
    if not profile_name and app.testing:
        profile_name = "testing"
    elif not profile_name and app.debug:
        profile_name = "development"

    # TODO: set default_config on the app and then call it as app.default_config so that
    # it can be easily overriden.
    config = default_config(app, profile_name) | env_config

    config_fpaths = app_config_fpaths(app, config)
    config = load_fpath_configs(app, config, config_fpaths, profile_name)
    config.update()

    config["_flac.config.fpaths"] = config_fpaths
    config["_flac.config.profile_name"] = profile_name

    return config


def load_fpath_configs(app, config, fpaths, config_prefix):
    for fpath in map(pathlib.Path, fpaths):
        if not fpath.exists():
            continue
        config = load_fpath_config(app, config, fpath, config_prefix)

    return config


def load_fpath_config(app, config, fpath, config_prefix):
    pymod_vars = {"__file__": str(fpath)}
    exec(fpath.read_bytes(), pymod_vars)

    # Default config has at least two purposes:
    # 1) Set defaults at the OS/User level while still being able to override at the app config
    #    level.
    # 2) Enable a default config without knowing the prefix name.  Helpful in deployed environments
    #    where only a single config exists and will be used by default.
    config = call_env_config(app, config, pymod_vars, "default")
    if config_prefix:
        config = call_env_config(app, config, pymod_vars, config_prefix)

    return config


def call_env_config(app, config, pymod_vars, config_prefix):
    callable_name = f"{config_prefix}_config"
    if callable_name in pymod_vars:
        return pymod_vars[callable_name](app, config)

    return config


def app_config_fpaths(app, config):
    config_fpaths = [
        # TODO: should work on Windows too
        f"/etc/{app.name}/config.py",
        osp.join(appdirs.user_config_dir(app.name), "config.py"),
        osp.join(app.root_path.parent.resolve(), f"{app.name}-config.py"),
    ]
    env_config_fpath = config.get("CONFIG_FILE")

    if env_config_fpath:
        config_fpaths.append(pathlib.Path(env_config_fpath).resolve())

    return config_fpaths


def default_config(app, config_profile):
    return {
        # TODO: shouldn't be here?
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }


def environ_key(app, key):
    return f"{app.name.upper()}_{key}"


def environ_config(app):
    retval = {}
    app_prefix = environ_key(app, "")
    for key, val in os.environ.items():
        if key.startswith(app_prefix):
            config_key = key.replace(app_prefix, "", 1)
            retval[config_key] = val

    return retval
