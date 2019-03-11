import logging
from functools import wraps
from time import time


def execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time()
        logging.info("--- STARTING EXECUTION of {} ---".format(func.__name__))
        result = func(*args, **kwargs)
        end = time()
        logging.info("--- EXECUTION TIME of {}: {} SECONDS ---".format(func.__name__, (end - start)))
        return result

    return wrapper
