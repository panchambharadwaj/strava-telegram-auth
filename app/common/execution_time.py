import logging
from functools import wraps
from time import time


def execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time()
        logging.info("--- STARTING EXECUTION ---")
        result = func(*args, **kwargs)
        end = time()
        logging.info("--- EXECUTION TIME: {} SECONDS ---".format(end - start))
        return result

    return wrapper
