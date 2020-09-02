import os.path as osp

from setuptools import setup, find_namespace_packages

cdir = osp.abspath(osp.dirname(__file__))
README = open(osp.join(cdir, 'README.md')).read()
CHANGELOG = ''  # open(osp.join(cdir, 'changelog.rst')).read()

version_fpath = osp.join(cdir, 'flac', 'version.py')
version_globals = {}
with open(version_fpath) as fo:
    exec(fo.read(), version_globals)

setup(
    name='flac',
    version=version_globals['VERSION'],
    description='Flask CLI library',
    long_description='\n\n'.join((README, CHANGELOG)),
    long_description_content_type='text/markdown',
    author='Randy Syring',
    author_email='randy.syring@level12.io',
    url='https://github.com/rsyring/flac',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    packages=find_namespace_packages(include=['flac.*']),
    py_modules=['flac_cc'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'appdirs',
        'arrow',
        'blazeutils',
        'flask',
        'flask_sqlalchemy',
        'psycopg2-binary',
        'python-json-logger',
        'requests',
        'sqlalchemy-utils',
    ],
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': [
            'flake8',
            'cookiecutter',
        ],
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'flac-cc=flac_cc:cli'
        ],
    },
)
