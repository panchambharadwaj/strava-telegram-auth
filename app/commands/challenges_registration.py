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
                    'challenge_ids': self.cadence90_odd_challenge_ids,
                    'query_insert': self.app_constants.QUERY_CHALLENGES_ODD_INSERT_VALUES,
                    'query_update': self.app_constants.QUERY_CHALLENGES_ODD_UPDATE_VALUES,
                    'payment_approval': True,
                    'payment_approval_details': self.cadence90_odd_payment
                },
                'even': {
                    'challenge_ids': self.cadence90_even_challenge_ids,
                    'query_insert': self.app_constants.QUERY_CHALLENGES_EVEN_INSERT_VALUES,
                    'query_update': self.app_constants.QUERY_CHALLENGES_EVEN_UPDATE_VALUES,
                    'payment_approval': False,
                    'payment_approval_details': self.cadence90_even_payment
                }
            },
            'bosch': {
                'odd': {
                    'challenge_ids': self.bosch_odd_challenge_ids,
                    'query_insert': self.app_constants.QUERY_CHALLENGES_BOSCH_ODD_INSERT_VALUES,
                    'query_update': self.app_constants.QUERY_CHALLENGES_BOSCH_ODD_UPDATE_VALUES,
                    'payment_approval': False,
                    'payment_approval_details': self.bosch_odd_payment
                },
                'even': {
                    'challenge_ids': self.bosch_even_challenge_ids,
                    'query_insert': self.app_constants.QUERY_CHALLENGES_BOSCH_EVEN_INSERT_VALUES,
                    'query_update': self.app_constants.QUERY_CHALLENGES_BOSCH_EVEN_UPDATE_VALUES,
                    'payment_approval': False,
                    'payment_approval_details': self.bosch_even_payment
                }
            }
        }

    @staticmethod
    def cadence90_odd_challenge_ids(athlete_details, form):
        utr = form.utr.data
        email = form.email.data
        phone = form.phone.data
        payment = False
        if athlete_details and athlete_details['odd_challenges'] and 'payment' in athlete_details['odd_challenges']:
            payment = athlete_details['odd_challenges']['payment']
        return {'utr': utr, 'phone': phone, 'email': email, 'payment': payment}

    @staticmethod
    def cadence90_odd_payment(athlete_details, access_info, form):
        payment_approval_message = payment_approval_callback_data = None
        if not athlete_details or not athlete_details['odd_challenges'] or 'payment' not in athlete_details[
            'odd_challenges'] or not \
                athlete_details['odd_challenges']['payment']:
            payment_approval_message = "{name} ({athlete_id}) registered for Cadence90 odd month challenge.\n\nUTR: {utr}\nPhone: {phone}\nEmail ID: {email}\n\nApprove payment?"
            payment_approval_callback_data = "pa_challenges_cadence90_odd_{athlete_id}"

            payment_approval_message = payment_approval_message.format(name=access_info['name'],
                                                                       athlete_id=access_info['athlete_id'],
                                                                       utr=form.utr.data,
                                                                       phone=form.phone.data,
                                                                       email=form.email.data)

            payment_approval_callback_data = payment_approval_callback_data.format(athlete_id=access_info['athlete_id'])

        return payment_approval_message, payment_approval_callback_data

    def cadence90_even_challenge_ids(self):
        pass

    def cadence90_even_payment(self, athlete_details, challenge_details):
        pass

    @staticmethod
    def bosch_odd_challenge_ids(athlete_details, form):
        challenge_ids = list()
        challenge_ids.append(form.challenge_one.data)
        challenge_ids.append(form.challenge_two.data)
        ntid = form.ntid.data
        email = form.email.data
        phone = form.phone.data
        location = form.location.data
        return {'id': challenge_ids, 'location': location, 'ntid': ntid, 'email': email, 'phone': phone}

    @staticmethod
    def bosch_odd_payment(athlete_details, challenge_details):
        pass

    @staticmethod
    def bosch_even_challenge_ids(athlete_details, form):
        challenge_ids = form.challenge_two.data
        ntid = form.ntid.data
        email = form.email.data
        phone = form.phone.data
        location = form.location.data
        return {'id': challenge_ids, 'location': location, 'ntid': ntid, 'email': email, 'phone': phone}

    def bosch_even_payment(self, athlete_details, challenge_details):
        pass

    def send_registration_for_payment_approval(self, company, month, athlete_details, access_info, form):
        payment_approval_message, payment_approval_callback_data = self.challenges_config[company][month][
            'payment_approval_details'](athlete_details, access_info, form)
        if payment_approval_message and payment_approval_callback_data:
            self.strava_telegram_webhooks.send_payment_approval_message(payment_approval_message,
                                                                        payment_approval_callback_data)
        else:
            self.strava_telegram_webhooks.update_challenges_stats(access_info['athlete_id'])

    def main(self, company, month, code, form):
        success = False
        access_info = self.strava_telegram_webhooks.token_exchange("challenges", code)
        if access_info:
            athlete_details = self.strava_telegram_webhooks.athlete_details_in_challenges(access_info['athlete_id'])
            query = self.challenges_config[company][month]['query_update'] if athlete_details else \
            self.challenges_config[company][month]['query_insert']
            challenge_ids = ujson.dumps(self.challenges_config[company][month]['challenge_ids'](athlete_details, form))
            if self.strava_telegram_webhooks.database_write(
                    query.format(athlete_id=access_info['athlete_id'], name=access_info['name'],
                                 access_token=self.aes_cipher.encrypt(access_info['access_token']),
                                 refresh_token=self.aes_cipher.encrypt(access_info['refresh_token']),
                                 expires_at=access_info['expires_at'], challenge_ids=challenge_ids)):
                if self.challenges_config[company][month]['payment_approval']:
                    self.send_registration_for_payment_approval(company, month, athlete_details, access_info, form)
                else:
                    self.strava_telegram_webhooks.update_challenges_stats(access_info['athlete_id'])

                message = self.app_constants.MESSAGE_NEW_CHALLENGES_REGISTRATION.format(
                    athlete_name=access_info['name'], company=company, month=month, data=challenge_ids)
                success = True
            else:
                message = "Failed to write {athlete_name}'s info into database.".format(
                    athlete_name=access_info['name'])

        else:
            message = "Failed to exchange token."

        logging.info(message)
        self.strava_telegram_webhooks.send_message(message)

        return success
