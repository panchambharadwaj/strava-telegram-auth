#  -*- encoding: utf-8 -*-

import os


class AppConstants(object):

    QUERY_INSERT_VALUES = "INSERT INTO strava_telegram_bot (athlete_id, name, access_token, refresh_token, " \
                          "expires_at, telegram_username, active, created) " \
                          "VALUES ({athlete_id}, '{name}', '{access_token}', '{refresh_token}', " \
                          "{expires_at}, '{telegram_username}', true, current_timestamp)"

    QUERY_UPDATE_VALUES = "UPDATE strava_telegram_bot " \
                          "SET name='{name}', access_token='{access_token}', " \
                          "refresh_token='{refresh_token}', expires_at={expires_at}, " \
                          "telegram_username='{telegram_username}', active=true, updated=now()" \
                          "where athlete_id={athlete_id}"

    QUERY_CHALLENGES_EVEN_INSERT_VALUES = "INSERT INTO strava_challenges (athlete_id, name, access_token, " \
                                          "refresh_token, expires_at, even_challenges, created) " \
                                          "VALUES ({athlete_id}, '{name}', '{access_token}', '{refresh_token}', " \
                                          "{expires_at}, '{challenge_ids}', current_timestamp)"

    QUERY_CHALLENGES_EVEN_UPDATE_VALUES = "UPDATE strava_challenges " \
                                          "SET name='{name}', access_token='{access_token}', " \
                                          "refresh_token='{refresh_token}', expires_at={expires_at}, " \
                                          "even_challenges='{challenge_ids}', updated=now() where athlete_id={athlete_id}"

    QUERY_CHALLENGES_ODD_INSERT_VALUES = "INSERT INTO strava_challenges (athlete_id, name, access_token, " \
                                         "refresh_token, expires_at, odd_challenges, created) " \
                                         "VALUES ({athlete_id}, '{name}', '{access_token}', '{refresh_token}', " \
                                         "{expires_at}, '{challenge_ids}', current_timestamp)"

    QUERY_CHALLENGES_ODD_UPDATE_VALUES = "UPDATE strava_challenges " \
                                         "SET name='{name}', access_token='{access_token}', " \
                                         "refresh_token='{refresh_token}', expires_at={expires_at}, " \
                                         "odd_challenges='{challenge_ids}', updated=now() where athlete_id={athlete_id}"

    API_TOKEN_EXCHANGE = "{host}/token/exchange/{code}"
    API_CHALLENGES_TOKEN_EXCHANGE = "{host}/token/exchange/challenges/{code}"
    API_ATHLETE_EXISTS = "{host}/athlete/exists/{athlete_id}"
    API_UPDATE_STATS = "{host}/stats/{athlete_id}"
    API_DATABASE_WRITE = "{host}/database/write"
    API_SHADOW_MESSAGE = "{host}/telegram/shadow_message"
    API_ATHLETE_DETAILS_IN_CHALLENGES = "{host}/challenges/athlete/{athlete_id}"
    API_ATHLETE_CALCULATE_CHALLENGES = "{host}challenges/stats/{athlete_id}"

    MESSAGE_NEW_REGISTRATION = "{athlete_name} registered with Telegram username `{telegram_username}`"
    MESSAGE_NEW_CHALLENGES_REGISTRATION = "{athlete_name} registered for {month} month's challenges.\n\nChallenge IDs: {challenge_ids}"


class AppVariables(object):
    crypt_key_length = int(os.environ.get('CRYPT_KEY_LENGTH'))
    crypt_key = os.environ.get('CRYPT_KEY')
    client_id = os.environ.get('CLIENT_ID')
    challenges_client_id = os.environ.get('CHALLENGES_CLIENT_ID')
    strava_auth_url = os.environ.get('STRAVA_AUTH_URL')
    strava_challenges_auth_url = os.environ.get('STRAVA_CHALLENGES_AUTH_URL')
    redirect_uri = os.environ.get('REDIRECT_URI')
    challenges_even_redirect_uri = os.environ.get('CHALLENGES_EVEN_REDIRECT_URI')
    challenges_odd_redirect_uri = os.environ.get('CHALLENGES_ODD_REDIRECT_URI')
    page_title = os.environ.get('PAGE_TITLE')
    challenges_even_page_title = os.environ.get('CHALLENGES_EVEN_PAGE_TITLE')
    challenges_odd_page_title = os.environ.get('CHALLENGES_ODD_PAGE_TITLE')
    secret_key = os.environ.get('SECRET_KEY')
    app_port = os.environ.get('APP_PORT')
    app_debug = os.environ.get('APP_DEBUG')
    app_host = os.environ.get('APP_HOST')
    bot_url = os.environ.get('BOT_URL')
    scout_monitor = os.environ.get('SCOUT_MONITOR')
    scout_key = os.environ.get('SCOUT_KEY')
    scout_name = os.environ.get('SCOUT_NAME')
    api_host = os.environ.get('API_HOST')
