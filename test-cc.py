import pathlib
import subprocess
import tempfile

from cookiecutter.main import cookiecutter

cc_dpath = str(pathlib.Path(__file__).resolve().parent / 'flac-app-cc')

with tempfile.TemporaryDirectory() as target_dpath:
    cookiecutter(cc_dpath, output_dir=target_dpath)
    subprocess.run(['pytest', target_dpath])
