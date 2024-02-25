import os
import os.path
from datetime import datetime, timedelta

def get_with_ttl(fname, ttl_seconds):
    try:
        s = os.stat(fname)
    except FileNotFoundError:
        return None

    m_time = datetime.fromtimestamp(s.st_mtime)
    if datetime.now() - m_time > timedelta(seconds=ttl_seconds):
        return None

    with open(fname, 'r') as f:
        return f.read()

def write(fname, contents):
    with open(fname, 'w') as f:
        f.write(contents)
