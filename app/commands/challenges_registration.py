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
        self.challenges_config = {
            'cadence90': {
                'odd': {
                    'challenge_ids': self.cadence90_odd,
                    'query_insert': self.app_constants.QUERY_CHALLENGES_ODD_INSERT_VALUES,
                    'query_update': self.app_constants.QUERY_CHALLENGES_ODD_UPDATE_VALUES
                },
                'even': {
                    'challenge_ids': self.cadence90_even,
                    'query_insert': self.app_constants.QUERY_CHALLENGES_EVEN_INSERT_VALUES,
                    'query_update': self.app_constants.QUERY_CHALLENGES_EVEN_UPDATE_VALUES
                }
            },
            'bosch': {
                'odd': {
                    'challenge_ids': self.bosch_odd,
                    'query_insert': self.app_constants.QUERY_CHALLENGES_BOSCH_ODD_INSERT_VALUES,
                    'query_update': self.app_constants.QUERY_CHALLENGES_BOSCH_ODD_UPDATE_VALUES
                },
                'even': {
                    'challenge_ids': self.bosch_even,
                    'query_insert': self.app_constants.QUERY_CHALLENGES_BOSCH_EVEN_INSERT_VALUES,
                    'query_update': self.app_constants.QUERY_CHALLENGES_BOSCH_EVEN_UPDATE_VALUES
                }
            }
        }

    @staticmethod
    def cadence90_odd(athlete_details, form):
        utr = form.utr.data
        email = form.email.data
        phone = form.phone.data
        payment = False
        if athlete_details:
            if 'payment' in athlete_details['odd_challenges']:
                payment = athlete_details['odd_challenges']['payment']
        return {'utr': utr, 'phone': phone, 'email': email, 'payment': payment}

    def cadence90_even(self):
        pass

    def bosch_odd(self):
        pass

    @staticmethod
    def bosch_even(athlete_details, form):
        challenge_ids = form.challenge_two.data
        ntid = form.ntid.data
        email = form.email.data
        phone = form.phone.data
        location = form.location.data
        return {'id': challenge_ids, 'location': location, 'ntid': ntid, 'email': email, 'phone': phone}

    def main(self, company, month, code, form):
        success = False
        access_info = self.strava_telegram_webhooks.token_exchange("challenges", code)
        if access_info:
            athlete_details = self.strava_telegram_webhooks.athlete_details_in_challenges(access_info['athlete_id'])
            if athlete_details:
                query = self.challenges_config[company][month]['query_update']
            else:
                query = self.challenges_config[company][month]['query_insert']

            challenge_ids = ujson.dumps(self.challenges_config[company][month]['challenge_ids'](athlete_details, form))

            if self.strava_telegram_webhooks.database_write(
                    query.format(athlete_id=access_info['athlete_id'], name=access_info['name'],
                                 access_token=self.aes_cipher.encrypt(access_info['access_token']),
                                 refresh_token=self.aes_cipher.encrypt(access_info['refresh_token']),
                                 expires_at=access_info['expires_at'], challenge_ids=challenge_ids)):
                success = True
                message = self.app_constants.MESSAGE_NEW_CHALLENGES_REGISTRATION.format(
                    athlete_name=access_info['name'], company=company, month=month, data=challenge_ids)
                self.strava_telegram_webhooks.update_challenges_stats(access_info['athlete_id'])
            else:
                message = "Failed to write {athlete_name}'s info into database.".format(
                    athlete_name=access_info['name'])

        else:
            message = "Failed to exchange token."

        logging.info(message)
        self.strava_telegram_webhooks.send_message(message)

        return success
