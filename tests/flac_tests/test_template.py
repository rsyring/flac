from os import environ
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib

import pytest


class TestFlacTemplate:
    @pytest.fixture()
    def repo_dpath(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @pytest.fixture()
    def clean_env(self) -> dict[str, str]:
        env = dict(environ)
        for key in ('UV_PYTHON', 'UV_PROJECT_ENVIRONMENT', 'VIRTUAL_ENV'):
            env.pop(key, None)

        return env

    @pytest.fixture()
    def template_source_dpath(self, tmp_path: Path, repo_dpath: Path) -> Path:
        source_dpath = tmp_path / 'flac-template-source'
        shutil.copytree(
            repo_dpath,
            source_dpath,
            ignore=shutil.ignore_patterns(
                '.git',
                '.nox',
                '.venv',
                '.pytest_cache',
                '.ruff_cache',
                '__pycache__',
            ),
        )
        return source_dpath

    def sub_run(self, *args: str, cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess:
        return subprocess.run(args, cwd=cwd, env=env, check=True, capture_output=True, text=True)

    def run_overlay(
        self,
        source_dpath: Path,
        target_dpath: Path,
        env: dict[str, str],
        *,
        project_name: str,
        generate_pyproject: bool,
    ) -> None:
        self.sub_run(
            sys.executable,
            '-m',
            'copier',
            'copy',
            '--trust',
            '--overwrite',
            '--defaults',
            '--data',
            f'project_name={project_name}',
            '--data',
            f'generate_pyproject={str(generate_pyproject).lower()}',
            str(source_dpath),
            str(target_dpath),
            cwd=source_dpath,
            env=env,
        )

    def test_generate_pyproject_standalone(
        self,
        tmp_path: Path,
        template_source_dpath: Path,
        clean_env,
    ):
        project_dpath = tmp_path / 'flac-standalone-app'
        self.run_overlay(
            template_source_dpath,
            project_dpath,
            clean_env,
            project_name='flac.standalone-app',
            generate_pyproject=True,
        )

        pyproject_fpath = project_dpath / 'pyproject.toml'
        assert pyproject_fpath.exists()
        assert not (project_dpath / 'hatch.toml').exists()
        assert (project_dpath / 'src/flac_standalone_app/__init__.py').exists()
        assert not (project_dpath / 'src/flac_standalone_app/version.py').exists()
        app_py = (project_dpath / 'src/flac_standalone_app/app.py').read_text()
        config_py = (project_dpath / 'src/flac_standalone_app-config.py').read_text()
        assert 'class FlacStandaloneApp(flac.app.FlacApp):' in app_py
        assert "f'flac_standalone_app{suffix}.sqlite3'" in config_py

        pyproject = pyproject_fpath.read_text()
        assert "build-backend = 'setuptools.build_meta'" in pyproject
        assert "'flac-standalone-app' = 'flac_standalone_app.cli:main'" in pyproject

        result = self.sub_run(
            'uv',
            'sync',
            '--group',
            'pytest',
            cwd=project_dpath,
            env=clean_env,
        )

        self.sub_run(
            'uv',
            'add',
            f'{template_source_dpath}[sqlalchemy]',
            '--editable',
            cwd=project_dpath,
            env=clean_env,
        )

        result = self.sub_run(
            '.venv/bin/python',
            '-m',
            'pytest',
            'tests/flac_standalone_app_tests',
            '-q',
            cwd=project_dpath,
            env=clean_env,
        )
        assert re.search(r'\b[1-9][0-9]* passed\b', result.stdout)

    def test_invalid_py_module_rejected(
        self,
        tmp_path: Path,
        template_source_dpath: Path,
        clean_env,
    ):
        project_dpath = tmp_path / 'flac-invalid-app'
        result = subprocess.run(
            [
                sys.executable,
                '-m',
                'copier',
                'copy',
                '--trust',
                '--overwrite',
                '--defaults',
                '--data',
                'project_name=flac-invalid-app',
                '--data',
                'py_module=bad.module',
                str(template_source_dpath),
                str(project_dpath),
            ],
            cwd=template_source_dpath,
            env=clean_env,
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode != 0
        assert 'py_module must be a valid Python package name' in result.stderr

    def test_skip_pyproject_generation(
        self,
        tmp_path: Path,
        template_source_dpath: Path,
        clean_env,
    ):
        project_dpath = tmp_path / 'flac-existing-app'
        project_dpath.mkdir()

        original_pyproject = """
[build-system]
requires = ['setuptools>=61']
build-backend = 'setuptools.build_meta'

[project]
name = 'flac-existing-app'
version = '0.1.0'
dependencies = []

[tool.setuptools]
package-dir = {'' = 'src'}

[tool.setuptools.packages.find]
where = ['src']
""".strip()
        (project_dpath / 'pyproject.toml').write_text(original_pyproject + '\n')
        original_pyproject_data = tomllib.loads(original_pyproject)

        self.run_overlay(
            template_source_dpath,
            project_dpath,
            clean_env,
            project_name='flac-existing-app',
            generate_pyproject=False,
        )

        pyproject = (project_dpath / 'pyproject.toml').read_text()
        pyproject_data = tomllib.loads(pyproject)
        assert pyproject_data['build-system'] == original_pyproject_data['build-system']
        assert pyproject_data['project']['name'] == original_pyproject_data['project']['name']
        assert pyproject_data['project']['version'] == original_pyproject_data['project']['version']
        assert pyproject_data['tool']['setuptools'] == original_pyproject_data['tool']['setuptools']
        assert 'scripts' not in pyproject_data['project']
        assert (project_dpath / 'src/flac_existing_app/__init__.py').exists()
