#  -*- encoding: utf-8 -*-

import logging
import traceback

from flask import Flask, request, redirect, render_template, url_for, flash
from scout_apm.flask import ScoutApm
from wtforms import Form, TextAreaField, validators

from app.clients.strava_telegram_webhooks import StravaTelegramWebhooks
from app.common.aes_cipher import AESCipher
from app.common.constants_and_variables import AppVariables, AppConstants
from app.common.shadow_mode import ShadowMode

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.os.environ.get('LOGGING_LEVEL'))
logger = logging.getLogger(__name__)

app_variables = AppVariables()
app_constants = AppConstants()
shadow_mode = ShadowMode()
aes_cipher = AESCipher(app_variables.crypt_key_length, app_variables.crypt_key)
strava_telegram_webhooks = StravaTelegramWebhooks()

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = app_variables.secret_key

ScoutApm(app)

app.config['SCOUT_MONITOR'] = app_variables.scout_monitor
app.config['SCOUT_KEY'] = app_variables.scout_key
app.config['SCOUT_NAME'] = app_variables.scout_name


class ReusableForm(Form):
    telegram_username = TextAreaField('Telegram Username:', validators=[validators.required()])


@app.route('/favicon.ico')
def hello():
    return redirect(url_for('static', filename='favicon.ico'), code=302)


@app.route("/")
def home():
    try:
        return "Welcome. Visit /register to register."
    except Exception:
        message = "Something went wrong. Exception: {exception}".format(exception=traceback.format_exc())
        logging.error(message)
        shadow_mode.send_message(message)


@app.route("/register")
def register():
    try:
        return redirect(app_variables.strava_auth_url.format(client_id=app_variables.client_id,
                                                             redirect_uri=app_variables.redirect_uri), code=302)
    except Exception:
        message = "Something went wrong. Exception: {exception}".format(exception=traceback.format_exc())
        logging.error(message)
        shadow_mode.send_message(message)


@app.route("/auth")
def auth_callback():
    try:
        code = request.args.get('code')
        return redirect(url_for('registration', code=code))
    except Exception:
        message = "Something went wrong. Exception: {exception}".format(exception=traceback.format_exc())
        logging.error(message)
        shadow_mode.send_message(message)


@app.route("/registration/<code>", methods=['GET', 'POST'])
def registration(code):
    try:
        form = ReusableForm(request.form)
        if request.method == 'POST':
            telegram_username = request.form['telegram_username'].strip()

            if form.validate():
                telegram_username = telegram_username[1:] if telegram_username.startswith('@') else telegram_username
                try:
                    access_info = strava_telegram_webhooks.token_exchange(code)
                    if not strava_telegram_webhooks.athlete_exists(access_info['athlete_id']):
                        query = app_constants.QUERY_INSERT_VALUES
                        logging.info("Adding new athlete {athlete_id}".format(athlete_id=access_info['athlete_id']))
                    else:
                        query = app_constants.QUERY_UPDATE_VALUES
                        logging.info("Updating athlete {athlete_id}".format(athlete_id=access_info['athlete_id']))

                    strava_telegram_webhooks.database_write(query.format(
                        athlete_id=access_info['athlete_id'],
                        name=access_info['name'],
                        access_token=aes_cipher.encrypt(access_info['access_token']),
                        refresh_token=aes_cipher.encrypt(access_info['refresh_token']),
                        expires_at=access_info['expires_at'],
                        telegram_username=telegram_username))

                    strava_telegram_webhooks.update_stats(access_info['athlete_id'])

                    shadow_mode.send_message(
                        app_constants.MESSAGE_NEW_REGISTRATION.format(athlete_name=access_info['name'],
                                                                      telegram_username=telegram_username))
                    return render_template('successful.html', page_title=app_variables.page_title,
                                           bot_url=app_variables.bot_url)

                except Exception:
                    logging.exception(
                        "Exception: {exception_traceback}".format(exception_traceback=traceback.format_exc()))
                    shadow_mode.send_message("Failed to register for Telegram username {telegram_username}".format(
                        telegram_username=telegram_username))
                    return render_template('failed.html', page_title=app_variables.page_title)
            else:
                flash('Telegram Username is Mandatory', 'Error')

        return render_template('registration.html', form=form, page_title=app_variables.page_title)

    except Exception:
        message = "Something went wrong. Exception: {exception}".format(exception=traceback.format_exc())
        logging.error(message)
        shadow_mode.send_message(message)


if __name__ == '__main__' and __package__ is None:
    app.run(host=app_variables.app_host, port=app_variables.app_port, debug=app_variables.app_debug)
