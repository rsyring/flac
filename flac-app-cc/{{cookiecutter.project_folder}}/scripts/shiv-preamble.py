"""
    This file gets bundled into the .pyz file and executed each time it's executed.
"""
# flake8: noqa
from flac.contrib.shiv import cleanup_shivs

# env and site_packages are injected into the runtime by shiv
cleanup_shivs(env, site_packages)
