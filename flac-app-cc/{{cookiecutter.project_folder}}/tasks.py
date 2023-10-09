from pathlib import Path

from invoke import task


base_dpath = Path(__file__).parent
reqs_dpath = base_dpath / 'requirements'
shiv_reqs_fpath = reqs_dpath / 'shiv.txt'

shiv_dpath = base_dpath / 'shiv'
pyz_fpath = base_dpath.joinpath('{{ cookiecutter.project_cli_bin }}.pyz')


@task(name='reqs-compile')
def reqs_compile(c, force=False):
    # TODO: this doesn't work because dev.txt will need to be compiled if common.txt
    # is newer.  But we only consider dev.txt.
    for base_name in ('common', 'dev', 'shiv'):
        in_fpath = reqs_dpath / f'{base_name}.in'
        txt_fpath = in_fpath.with_suffix('.txt')

        if not force and txt_fpath.exists() and txt_fpath.stat().st_mtime >= in_fpath.stat().st_mtime:
            print(f'{txt_fpath.name} newer than {in_fpath.name}')
            continue

        c.run(f'pip-compile --quiet --output-file {txt_fpath} {in_fpath}', echo=True)


@task(name='reqs-sync')
def reqs_sync(c, sync_fname='dev.txt', no_compile=False):
    if not no_compile:
        reqs_compile(c)

    c.run(f'pip-sync --quiet {reqs_dpath / sync_fname}', echo=True)
    c.run(f'pip --quiet install -e {base_dpath}', echo=True)


@task(name='shiv-build')
def shiv_build(c, force_deps=False):
    # Avoid dep needing to be installed if this task isn't used.  Also easier to delete this
    # task if not used.
    import shiv_utils

    shiv_utils.build(
        base_dpath,
        'requirements/shiv.txt',
        '{{ cookiecutter.project_pymod }}',
        '{{ cookiecutter.project_pymod }}.app:cli',
        pyz_fpath=pyz_fpath,
        preamble_fpath=shiv_dpath.joinpath('preamble.py'),
        force_deps=force_deps,
    )

    print(f'Saved at {pyz_fpath.name}')
