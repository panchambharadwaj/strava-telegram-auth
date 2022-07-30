#  -*- encoding: utf-8 -*-

import json
import logging
import traceback

import requests

from common.constants_and_variables import AppVariables, AppConstants


class StravaTelegramWebhooksResource:

    def __init__(self):
        self.app_variables = AppVariables()
        self.app_constants = AppConstants()
        self.host = self.app_variables.api_host

    def bot_registration(self, strava_code, telegram_username):
        result = False
        data = json.dumps(
            {
                "stravaCode": strava_code,
                "telegramUsername": telegram_username
            }
        )
        endpoint = self.app_constants.API_BOT_REGISTRATION.format(host=self.host)
        try:
            logging.info("Requesting Bot registration: %s", telegram_username)
            response = requests.post(endpoint, data=data, auth=("bot", self.app_variables.bot_password),
                                     headers={"Content-Type": "application/json"})
            logging.info("Response status code: %s", response.status_code)
        except Exception:
            logging.error(traceback.format_exc())
        else:
            if response.status_code == 200:
                result = True

        return result
