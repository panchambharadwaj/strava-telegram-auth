#  -*- encoding: utf-8 -*-

import logging

import ujson

from app.common.aes_cipher import AESCipher
from app.common.constants_and_variables import AppConstants, AppVariables
from app.resources.strava_telegram_webhooks import StravaTelegramWebhooksResource


class ChallengesRegistration:

    def __init__(self):
        self.app_constants = AppConstants()
        self.app_variables = AppVariables()
        self.strava_telegram_webhooks = StravaTelegramWebhooksResource()
        self.aes_cipher = AESCipher(self.app_variables.crypt_key_length, self.app_variables.crypt_key)

    def main(self, challenge_ids, month, code, category):
        logging.info("Challenge IDs: %s. Month: %s", challenge_ids, month)
        success = False
        access_info = self.strava_telegram_webhooks.token_exchange(category, code)
        if access_info:
            athlete_details = self.strava_telegram_webhooks.athlete_details_in_challenges(access_info['athlete_id'])
            if athlete_details:
                query = self.app_constants.QUERY_CHALLENGES_EVEN_UPDATE_VALUES if month == "even" else self.app_constants.QUERY_CHALLENGES_ODD_UPDATE_VALUES
            else:
                query = self.app_constants.QUERY_CHALLENGES_EVEN_INSERT_VALUES if month == "even" else self.app_constants.QUERY_CHALLENGES_ODD_INSERT_VALUES

            if self.strava_telegram_webhooks.database_write(
                    query.format(athlete_id=access_info['athlete_id'], name=access_info['name'],
                                 access_token=self.aes_cipher.encrypt(access_info['access_token']),
                                 refresh_token=self.aes_cipher.encrypt(access_info['refresh_token']),
                                 expires_at=access_info['expires_at'], challenge_ids=ujson.dumps(challenge_ids))):
                success = True
                message = self.app_constants.MESSAGE_NEW_CHALLENGES_REGISTRATION.format(
                    athlete_name=access_info['name'], month=month, challenge_ids=challenge_ids)
                self.strava_telegram_webhooks.update_challenges_stats(access_info['athlete_id'])
            else:
                message = "Failed to write {athlete_name}'s info into database.".format(
                    athlete_name=access_info['name'])

        else:
            message = "Failed to exchange token."

        logging.info(message)
        self.strava_telegram_webhooks.send_message(message)

        return success

    def bosch(self, challenge_ids, location, ntid, email, phone, month, code, category):
        logging.info("Challenge IDs: %s. Month: %s. Location: %s", challenge_ids, month, location)
        success = False
        access_info = self.strava_telegram_webhooks.token_exchange(category, code)
        if access_info:
            athlete_details = self.strava_telegram_webhooks.athlete_details_in_challenges(access_info['athlete_id'])
            if athlete_details:
                query = self.app_constants.QUERY_CHALLENGES_BOSCH_EVEN_UPDATE_VALUES if month == "even" else self.app_constants.QUERY_CHALLENGES_BOSCH_ODD_UPDATE_VALUES
            else:
                query = self.app_constants.QUERY_CHALLENGES_BOSCH_EVEN_INSERT_VALUES if month == "even" else self.app_constants.QUERY_CHALLENGES_BOSCH_ODD_INSERT_VALUES

            if self.strava_telegram_webhooks.database_write(
                    query.format(athlete_id=access_info['athlete_id'], name=access_info['name'],
                                 access_token=self.aes_cipher.encrypt(access_info['access_token']),
                                 refresh_token=self.aes_cipher.encrypt(access_info['refresh_token']),
                                 expires_at=access_info['expires_at'],
                                 challenge_ids=ujson.dumps(
                                     {'id': challenge_ids, 'location': location, 'ntid': ntid, 'email': email,
                                      'phone': phone}))):
                success = True
                message = self.app_constants.MESSAGE_NEW_BOSCH_CHALLENGES_REGISTRATION.format(
                    athlete_name=access_info['name'], month=month, challenge_ids=challenge_ids, location=location,
                    ntid=ntid, email=email, phone=phone)
                self.strava_telegram_webhooks.update_challenges_stats(access_info['athlete_id'])
            else:
                message = "Failed to write {athlete_name}'s info into database.".format(
                    athlete_name=access_info['name'])

        else:
            message = "Failed to exchange token."

        logging.info(message)
        self.strava_telegram_webhooks.send_message(message)

        return success
