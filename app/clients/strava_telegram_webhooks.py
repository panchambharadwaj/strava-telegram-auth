#  -*- encoding: utf-8 -*-
import logging
import traceback

import requests

from app.common.constants_and_variables import AppVariables, AppConstants


class StravaTelegramWebhooks(object):

    def __init__(self):
        self.app_variables = AppVariables()
        self.app_constants = AppConstants()
        self.host = self.app_variables.api_host

    def token_exchange(self, code):
        result = {}
        endpoint = self.app_constants.API_TOKEN_EXCHANGE.format(host=self.host, code=code)
        try:
            response = requests.post(endpoint)
        except Exception:
            logging.error(traceback.format_exc())
        else:
            if response.status_code == 200:
                result = response.json()

        return result if result != {} else False

    def athlete_exists(self, athlete_id):
        result = False
        endpoint = self.app_constants.API_ATHLETE_EXISTS.format(host=self.host, athlete_id=athlete_id)
        try:
            response = requests.get(endpoint)
        except Exception:
            logging.error(traceback.format_exc())
        else:
            if response.status_code == 200:
                result = True

        return result

    def update_stats(self, athlete_id):
        result = False
        endpoint = self.app_constants.API_UPDATE_STATS.format(host=self.host, athlete_id=athlete_id)
        try:
            response = requests.post(endpoint)
        except Exception:
            logging.error(traceback.format_exc())
        else:
            if response.status_code == 200:
                result = True

        return result

    def database_write(self, query):
        result = False
        endpoint = self.app_constants.API_DATABASE_WRITE.format(host=self.host, query=query)
        try:
            response = requests.post(endpoint)
        except Exception:
            logging.error(traceback.format_exc())
        else:
            if response.status_code == 200:
                result = True

        return result
