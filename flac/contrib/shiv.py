import logging
import os
import pathlib
import subprocess
import shutil
import sys

log = logging.getLogger(__name__)

SHIV_STDERR_DEBUG = 'SHIV_STDERR_DEBUG' in os.environ


def log_debug(msg):
    """ Log to stderr based on environment variable

        The preamble will usually get called so early in the process setup that nothing else will
        have had a chance to run yet, not even code that sets up Python logging.  This permits
        logging to stderr if the environment variable SHIV_STDERR_DEBUG has been set.

        But, we also pass the value on to the Python logging library in case the normal logging
        faculties have been used.
    """
    log.debug(msg)
    if SHIV_STDERR_DEBUG:
        print(msg, file=sys.stderr)


def auto_cleanup():
    env, site_packages_dpath = shiv_info_callstack()
    if env is None:
        log_debug('shiv environment not detected')
        return
    cleanup_shivs(env, site_packages_dpath)


def shiv_info_callstack():
    """ Maybe more brittle than shiv_info() but about 25x faster. """
    try:
        for x in range(1000):
            f = sys._getframe(x)
            if f.f_code.co_name == 'bootstrap':
                site_packages_dpath = pathlib.Path(f.f_locals['site_packages'])
                return f.f_locals['env'], site_packages_dpath
    except ValueError as e:
        if 'call stack is not deep enough' not in str(e):
            raise
        return None, None


def cleanup_shivs(env, site_packages_dpath):
    cache_dpath = site_packages_dpath.parent
    build_id = env.build_id

    dname_prefix = cache_dpath.name[0:-64]
    dname_length = len(cache_dpath.name)
    cache_root_dpath = cache_dpath.parent

    for dpath in cache_root_dpath.iterdir():
        dir_name = dpath.name

        if build_id in dir_name \
                or len(dir_name) != dname_length \
                or dir_name[0:-64] != dname_prefix \
                or not dpath.is_dir():
            continue

        log_debug(f'Deleting {dpath} and lock file')
        shutil.rmtree(dpath)

        lock_fpath = pathlib.Path(cache_root_dpath, f'.{dpath.stem}_lock')

        if lock_fpath.exists():
            # Don't use missing_ok param to unlink b/c it's Python 3.8 only
            lock_fpath.unlink()


def sub_run(*args, **kwargs):
    kwargs['check'] = True
    return subprocess.run(args, **kwargs)


def build(scripts_dpath, app_name, pybin, skip_deps, pyz_name=None):
    pyz_name = pyz_name or app_name
    proj_dpath = scripts_dpath.parent
    app_dpath = proj_dpath / app_name
    reqs_dpath = proj_dpath / 'requirements'
    reqs_fpath = reqs_dpath / 'common.txt'
    dist_dpath = proj_dpath / 'dist'
    dist_app_dpath = dist_dpath / app_name
    pyz_fpath = proj_dpath / f'{pyz_name}.pyz'
    preamble_fpath = scripts_dpath / 'shiv-preamble.py'

    if not skip_deps:
        # cleanup all present dependency files to avoid accidental junk in the build
        if dist_dpath.exists():
            shutil.rmtree(dist_dpath)

        # install dependencies
        sub_run(pybin, '-m', 'pip', 'install', '-r', reqs_fpath, '--target', dist_dpath)
    else:
        if dist_app_dpath.exists():
            # only remove the app's files so they can be replaced
            shutil.rmtree(dist_app_dpath)

    shutil.copytree(app_dpath, dist_app_dpath, dirs_exist_ok=True)

    sub_run(
        'shiv',
        '--compile-pyc',
        '--compressed',
        '--site-packages', dist_dpath,
        '--python', f'/usr/bin/env {pybin}',
        '--output-file', pyz_fpath,
        '--entry-point', f'{app_name}.app:cli',
        '--preamble', preamble_fpath,
    )
