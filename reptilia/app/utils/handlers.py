from functools import wraps

import logging

def exception_handler(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            r = f(*args, **kwargs)
        except Exception as e:
            logging.error(f'::{f.__module__}::{f.__name__}: {e}')
            r = {'status': False}

        return r

    return wrapper
