from pathlib import Path

import nox


package_path = Path.cwd()

# NOTE: uv is much faster at creating venvs and generally compatible with pip.
# Pip compat: https://github.com/astral-sh/uv/blob/main/PIP_COMPATIBILITY.md
nox.options.default_venv_backend = 'uv'


def pip_sync(session, path):
    session.run('uv', 'pip', 'sync', path)


@nox.session
def tests(session: nox.Session):
    session.install('-r', 'requirements/base.txt')
    session.install('-e', '.')
    session.run(
        'pytest',
        '-ra',
        '--tb=native',
        '--strict-markers',
        '--cov=flac',
        '--cov-config=.coveragerc',
        '--cov-report=xml',
        '--no-cov-on-fail',
        f'--junit-xml={package_path}/ci/test-reports/{session.name}.pytests.xml',
        'src/flac_tests',
        *session.posargs,
    )


@nox.session
def precommit(session: nox.Session):
    session.install('-c', 'requirements/dev.txt', 'pre-commit')
    session.run(
        'pre-commit',
        'run',
        '--all-files',
    )


@nox.session
def audit(session: nox.Session):
    # Much faster to install the deps first and have pip-audit run against the venv
    pip_sync(session, 'requirements/dev.txt')
    session.run(
        'pip-audit',
        '--desc',
        '--skip-editable',
    )
