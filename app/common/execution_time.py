import logging
from functools import wraps
from time import time


def execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time()
        logging.info("--- STARTING EXECUTION of %s ---", func.__name__)
        result = func(*args, **kwargs)
        end = time()
        logging.info("--- EXECUTION TIME of %s: %s SECONDS ---", func.__name__, end - start)
        return result

    return wrapper
