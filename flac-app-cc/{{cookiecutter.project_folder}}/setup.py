from setuptools import setup


setup(
    name='{{ cookiecutter.project_name }}',
    entry_points={
        'console_scripts': [
            '{{ cookiecutter.project_dashed }}={{cookiecutter.project_namespace}}.app:cli'
        ],
    },
)
