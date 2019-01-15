#  -*- encoding: utf-8 -*-

import os


class AppConstants(object):
    QUERY_CREATE_TABLE = '''create table strava_telegram_bot(
        id serial NOT NULL,
        athlete_id INTEGER PRIMARY KEY,
        name VARCHAR NOT NULL,
        email VARCHAR NOT NULL,
        access_token VARCHAR NOT NULL,
        refresh_token VARCHAR NOT NULL,
        expires_at INTEGER NOT NULL,
        telegram_username VARCHAR NOT NULL,
        strava_data json DEFAULT NULL,
        update_indoor_ride BOOLEAN NOT NULL DEFAULT FALSE,
        update_indoor_ride_data json DEFAULT NULL,
        created timestamp NOT NULL,
        updated timestamp default current_timestamp NOT NULL
        );'''

    QUERY_ATHLETE_EXISTS = "select count(*) from strava_telegram_bot where athlete_id={athlete_id}"

    QUERY_INSERT_VALUES = "INSERT INTO strava_telegram_bot (athlete_id, name, email, access_token, refresh_token, " \
                          "expires_at, telegram_username, created) " \
                          "VALUES ({athlete_id}, '{name}', '{email}', '{access_token}', '{refresh_token}', " \
                          "{expires_at}, '{telegram_username}', current_timestamp)"

    QUERY_UPDATE_VALUES = "UPDATE strava_telegram_bot " \
                          "SET name='{name}', email='{email}', access_token='{access_token}', " \
                          "refresh_token='{refresh_token}', expires_at={expires_at}, " \
                          "telegram_username='{telegram_username}', updated=now()" \
                          "where athlete_id={athlete_id}"

    API_TOKEN_EXCHANGE = "https://www.strava.com/oauth/token"
    API_WEBHOOK_UPDATE_STATS = "https://strava-telegram-webhooks-stage.herokuapp.com/stats/{athlete_id}"
    API_TELEGRAM_SEND_MESSAGE = "https://api.telegram.org/bot{bot_token}/sendMessage"


class AppVariables(object):
    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET')
    strava_auth_url = os.environ.get('STRAVA_AUTH_URL')
    redirect_uri = os.environ.get('REDIRECT_URI')
    page_title = os.environ.get('PAGE_TITLE')
    secret_key = os.environ.get('SECRET_KEY')
    app_port = os.environ.get('APP_PORT')
    database_url = os.environ.get('DATABASE_URL')
    app_debug = os.environ.get('APP_DEBUG')
    app_host = os.environ.get('APP_HOST')
    bot_url = os.environ.get('BOT_URL')
    telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    shadow_mode = os.environ.get('SHADOW_MODE')
    shadow_mode_chat_id = os.environ.get('SHADOW_MODE_CHAT_ID')
