#  -*- encoding: utf-8 -*-

import logging

from app.common.aes_cipher import AESCipher
from app.common.constants_and_variables import AppConstants, AppVariables
from app.resources.strava_telegram_webhooks import StravaTelegramWebhooksResource


class BotRegistration:

    def __init__(self):
        self.app_constants = AppConstants()
        self.app_variables = AppVariables()
        self.strava_telegram_webhooks = StravaTelegramWebhooksResource()
        self.aes_cipher = AESCipher(self.app_variables.crypt_key_length, self.app_variables.crypt_key)

    def main(self, telegram_username, code, category):
        success = False
        telegram_username = telegram_username[1:] if telegram_username.startswith('@') else telegram_username
        access_info = self.strava_telegram_webhooks.token_exchange(category, code)
        if access_info:
            athlete_exists = self.strava_telegram_webhooks.athlete_exists(access_info['athlete_id'])
            if not athlete_exists:
                query = self.app_constants.QUERY_INSERT_VALUES
                logging.info("New athlete.")
            else:
                query = self.app_constants.QUERY_UPDATE_VALUES
                logging.info("Existing athlete.")

            result = self.strava_telegram_webhooks.database_write(query.format(
                athlete_id=access_info['athlete_id'],
                name=access_info['name'],
                access_token=self.aes_cipher.encrypt(access_info['access_token']),
                refresh_token=self.aes_cipher.encrypt(access_info['refresh_token']),
                expires_at=access_info['expires_at'],
                telegram_username=telegram_username))
            if result:
                success = True
                result = self.strava_telegram_webhooks.update_stats(access_info['athlete_id'])
                if result:
                    message = self.app_constants.MESSAGE_NEW_REGISTRATION.format(athlete_name=access_info['name'],
                                                                                 telegram_username=telegram_username)
                else:
                    message = "Failed to request to update stats for {athlete_name}..".format(
                        athlete_name=access_info['name'])
            else:
                message = "Failed to write {athlete_name}'s info into database.".format(
                    athlete_name=access_info['name'])
        else:
            message = "Failed to exchange token for {telegram_username}.".format(telegram_username=telegram_username)

        logging.info(message)
        self.strava_telegram_webhooks.shadow_message(message)

        return success
