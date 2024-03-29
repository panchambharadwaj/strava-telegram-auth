#  -*- encoding: utf-8 -*-

import os


class AppConstants:
    API_BOT_REGISTRATION = "{host}/v1/bot/athletes"


class AppVariables:
    client_id = os.environ.get('CLIENT_ID')
    strava_auth_url = os.environ.get('STRAVA_AUTH_URL')
    strava_auth_scope = os.environ.get('STRAVA_AUTH_SCOPE')
    redirect_uri = os.environ.get('REDIRECT_URI')
    page_title = "Strava Authentication"
    secret_key = os.environ.get('SECRET_KEY')
    bot_url = os.environ.get('BOT_URL')
    api_host = os.environ.get('API_HOST')
    bot_password = os.environ.get('BOT_PASSWORD')
