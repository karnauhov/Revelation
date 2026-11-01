"""Source-loaded startup guard: bypass old bytecode without creating new caches.

Entry scripts execute this file directly before importing the coordinator. A -B
flag alone still reads existing .pyc files, including truncated files left by a
previous full disk. A fresh, never-written prefix makes imports use .py sources.
"""

import os
import sys

sys.dont_write_bytecode = True
sys.pycache_prefix = os.path.join(
    os.environ.get('TMPDIR') or os.environ.get('TEMP') or '/tmp',
    '.ai11-unused-python-cache', str(os.getpid()) + '-' + os.urandom(8).hex())
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['PYTHONPYCACHEPREFIX'] = sys.pycache_prefix
