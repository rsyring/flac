#!/bin/env python
import pathlib
import subprocess

import click
from cookiecutter.main import cookiecutter

flac_proj_dpath = pathlib.Path(__file__).resolve().parent
cc_dpath = flac_proj_dpath.joinpath('flac-app-cc')

@click.group()
def cli():
    pass


@cli.command()
@click.argument('target_dpath', default='.')
@click.option('--run-tests', is_flag=True, default=False)
@click.option('--no-input', is_flag=True, default=False)
@click.option('--overwrite', is_flag=True, default=False)
@click.option('--flac-rec-local', is_flag=True, default=False)
def create(target_dpath, run_tests, no_input, overwrite, flac_rec_local):
    extra_context = {}
    if flac_rec_local:
        extra_context['flac_req_spec'] = f'-e {flac_proj_dpath}'

    result_dpath = cookiecutter(
        str(cc_dpath), output_dir=target_dpath, no_input=no_input, overwrite_if_exists=overwrite,
        extra_context=extra_context
    )
    result_dpath = pathlib.Path(result_dpath)
    print('created project at:', result_dpath)

    sub_run('make', cwd=result_dpath / 'requirements')
    sub_run('docker-compose', 'up', '-d', cwd=result_dpath)
    sub_run('tox', cwd=result_dpath, check=False)
    sub_run('docker-compose', 'down', cwd=result_dpath)


def sub_run(*args, **kwargs):
    kwargs.setdefault('check', True)
    return subprocess.run(args, **kwargs)


if __name__ == '__main__':
    cli()
