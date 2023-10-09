import subprocess
import shlex

# Resolve chicken & egg problem with using invoke to compile & sync reqs.
cmd = 'pip', 'install', '--quiet', '-U', 'pip', 'pip-tools', 'invoke'
print('Running:', shlex.join(cmd))
subprocess.run(cmd, check=True)
