# -*- coding: utf-8 -*-

import subprocess
import errno

VALID_BINARIES = ['ffmpeg', 'avconv']
BINARY = None

# Figuring out which binary to use
for binary in VALID_BINARIES:
    try:
        subprocess.check_output([binary], stderr=subprocess.STDOUT)
    except OSError as e:
        if e.errno == errno.ENOENT:
            continue

        BINARY = binary
        break
    except subprocess.CalledProcessError:
        BINARY = binary
        break

if BINARY is None:
    raise Exception('No valid binary could be found. '
                    'One of %s must be installed.'
                    % ', '.join(VALID_BINARIES))
