#  -*- encoding: utf-8 -*-

import logging
import traceback

import requests
import ujson

from app.common.constants_and_variables import AppVariables, AppConstants


class StravaTelegramWebhooksResource:

    def __init__(self):
        self.app_variables = AppVariables()
        self.app_constants = AppConstants()
        self.host = self.app_variables.api_host

    def token_exchange(self, code):
        result = {}
        endpoint = self.app_constants.API_TOKEN_EXCHANGE.format(host=self.host, code=code)
        try:
            logging.info("Requesting token exchange..")
            response = requests.post(endpoint)
            logging.info("Response status code: %s", response.status_code)
        except Exception:
            logging.error(traceback.format_exc())
        else:
            if response.status_code == 200:
                result = response.json()

        return result if result != {} else False

    def token_exchange_for_challenges(self, code):
        result = {}
        endpoint = self.app_constants.API_CHALLENGES_TOKEN_EXCHANGE.format(host=self.host, code=code)
        try:
            logging.info("Requesting token exchange for challenges..")
            response = requests.post(endpoint)
            logging.info("Response status code: %s", response.status_code)
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
            logging.info("Checking if athlete %s already exists..", athlete_id)
            response = requests.get(endpoint)
            logging.info("Response status code: %s", response.status_code)
        except Exception:
            logging.error(traceback.format_exc())
        else:
            if response.status_code == 200:
                result = True

        return result

    def athlete_details_in_challenges(self, athlete_id):
        result = False
        endpoint = self.app_constants.API_ATHLETE_DETAILS_IN_CHALLENGES.format(host=self.host, athlete_id=athlete_id)
        try:
            logging.info("Fetching athlete details for %s from challenges..", athlete_id)
            response = requests.get(endpoint)
            logging.info("Response status code: %s", response.status_code)
        except Exception:
            logging.error(traceback.format_exc())
        else:
            if response.status_code == 200:
                result = response.json()

        return result

    def update_stats(self, athlete_id):
        result = False
        endpoint = self.app_constants.API_UPDATE_STATS.format(host=self.host, athlete_id=athlete_id)
        try:
            logging.info("Sending request to update stats for %s", athlete_id)
            response = requests.post(endpoint)
            logging.info("Response status code: %s", response.status_code)
        except Exception:
            logging.error(traceback.format_exc())
        else:
            if response.status_code == 200:
                result = True

        return result

    def update_challenges_stats(self, athlete_id):
        result = False
        endpoint = self.app_constants.API_ATHLETE_CALCULATE_CHALLENGES.format(host=self.host, athlete_id=athlete_id)
        try:
            logging.info("Sending request to update challenges stats for %s", athlete_id)
            response = requests.post(endpoint)
            logging.info("Response status code: %s", response.status_code)
        except Exception:
            logging.error(traceback.format_exc())
        else:
            if response.status_code == 200:
                result = True

        return result

    def database_write(self, query):
        result = False
        endpoint = self.app_constants.API_DATABASE_WRITE.format(host=self.host)
        data = ujson.dumps({"query": query})
        try:
            logging.info("Requesting write operation to the database..")
            response = requests.post(endpoint, data=data, headers={"Content-Type": "application/json"})
            logging.info("Response status code: %s", response.status_code)
        except Exception:
            logging.error(traceback.format_exc())
        else:
            if response.status_code == 200:
                result = True

        return result

    def shadow_message(self, message):
        result = False
        endpoint = self.app_constants.API_SHADOW_MESSAGE.format(host=self.host)
        data = ujson.dumps({"message": message})
        try:
            logging.info("Requesting to send shadow message..")
            response = requests.post(endpoint, data=data, headers={"Content-Type": "application/json"})
            logging.info("Response status code: %s", response.status_code)
        except Exception:
            logging.error(traceback.format_exc())
        else:
            if response.status_code == 200:
                result = True

        return result
