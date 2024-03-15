import os
import os.path
from datetime import datetime, timedelta
import tempfile
import functools

def _get_abs_path(fname):
     return os.path.join(tempfile.gettempdir(), fname)

def get_with_ttl(fname, ttl_seconds):
    abs_path = _get_abs_path(fname)
    try:
        s = os.stat(abs_path)
    except FileNotFoundError:
        return None

    m_time = datetime.fromtimestamp(s.st_mtime)
    if datetime.now() - m_time > timedelta(seconds=ttl_seconds):
        return None

    with open(abs_path, 'r') as f:
        return f.read()

def write(fname, contents):
    abs_path = _get_abs_path(fname)
    with open(abs_path, 'w') as f:
        f.write(contents)

def with_file_cache(fname, ttl_seconds=60*60):
    def decorator(f):
        @functools.wraps(f)
        def wrap(*args, **kwargs):
            if res := get_with_ttl(fname, ttl_seconds):
                return res
            out = f(*args, **kwargs)
            write(fname, out)
            return out

        return wrap

def call_with_cache(fname, f, *args, **kwargs):
    ttl_seconds = kwargs.get('ttl_seconds', 60*60)
    if res := get_with_ttl(fname, ttl_seconds):
        return res
    out = f(*args, **kwargs)
    write(fname, out)
    return out
