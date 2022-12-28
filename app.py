#  -*- encoding: utf-8 -*-

import logging
import traceback

from flask import Flask, request, redirect, render_template, url_for, flash

from common.constants_and_variables import AppVariables
from common.forms import RegistrationBot
from resources.strava_telegram_webhooks import StravaTelegramWebhooksResource

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app_variables = AppVariables()
strava_telegram_webhooks = StravaTelegramWebhooksResource()

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = app_variables.secret_key


@app.route('/favicon.ico')
def hello():
    return redirect(url_for('static', filename='favicon.ico'), code=302)


@app.route("/")
def home():
    return "Welcome. Visit /register to register."


@app.route("/register")
def register():
    strava_auth_url = app_variables.strava_auth_url.format(client_id=app_variables.client_id,
                                                           redirect_uri=app_variables.redirect_uri,
                                                           scope=app_variables.strava_auth_scope)
    return redirect(strava_auth_url, code=302)


@app.route("/auth")
def auth_callback():
    code = request.args.get('code')
    permissions = request.args.get('scope')
    if permissions != app_variables.strava_auth_scope:
        page_title = app_variables.page_title
        strava_auth_url = app_variables.strava_auth_url.format(client_id=app_variables.client_id,
                                                               redirect_uri=app_variables.redirect_uri,
                                                               scope=app_variables.strava_auth_scope)
        logging.warning("Insufficient permissions.")
        return render_template('failed_permissions.html', page_title=page_title, auth_link=strava_auth_url)
    else:
        return redirect(url_for('registration', code=code))


@app.route("/registration/<code>", methods=['GET', 'POST'])
def registration(code):
    try:
        form = RegistrationBot(request.form)
        if request.method == 'POST':
            telegram_username = request.form['telegram_username'].strip()
            if form.validate():
                logging.info("Registering Telegram user: %s..", telegram_username)
                telegram_username = telegram_username[1:] if telegram_username.startswith('@') else telegram_username
                if strava_telegram_webhooks.bot_registration(code, telegram_username):
                    return render_template('successful.html', page_title=app_variables.page_title,
                                           bot_url=app_variables.bot_url)
                else:
                    return render_template('failed.html', page_title=app_variables.page_title)
            else:
                logging.error("User did not enter Telegram Username")
                flash('Telegram Username is Mandatory', 'Error')

        logging.info("Not a POST call. Redirecting to registration page..")
        return render_template('registration.html', form=form, page_title=app_variables.page_title)
    except Exception:
        logging.error("Something went wrong. Exception: {exception}".format(exception=traceback.format_exc()))


if __name__ == '__main__' and __package__ is None:
    from waitress import serve
    serve(app, host='0.0.0.0', port=8020)
