import collections
import datetime
import time
from functools import wraps


def func_exec_timer(func):
    @wraps(func)
    def calculate_time(*args, **kwargs):
        before = time.time()
        output = func(*args, **kwargs)
        print(f"\'{func.__name__}\' took \'{time.time() - before}\' seconds")
        return output

    return calculate_time


def default_to_regular(d):
    if isinstance(d, collections.defaultdict) or isinstance(d, dict):
        return {k: default_to_regular(v) for k, v in d.items()}
    else:
        return d


def convert_unix_timestamp(unix_timestamp):
    """Converts unix timestamp L{int} to L{datetime.datetime}."""
    return datetime.datetime.fromtimestamp(unix_timestamp / 1000.0, tz=datetime.timezone.utc)
