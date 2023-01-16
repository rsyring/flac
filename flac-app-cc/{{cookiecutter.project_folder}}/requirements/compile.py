#!/usr/bin/env python3
"""  """

from pathlib import Path
import subprocess

reqs_dpath = Path(__file__).parent


def sub_run(*args, **kwargs):
    kwargs['check'] = True
    return subprocess.run(args, cwd=reqs_dpath, **kwargs)


# Can run make from a different directory now.  i.e. `./requirements/compile.py`
sub_run('make')

# Shiv can't use editable versions.  If not using local dev version of flac, this can be safely
# removed.  Although it shouldn't hurt anything to leave it.
sub_run('sed', '-i', r's/^-e \(file:.*\/flac.*\)/\1/', 'shiv.txt')
