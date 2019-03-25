#  -*- encoding: utf-8 -*-

import logging
import traceback

from flask import Flask, request, redirect, render_template, url_for, flash
from scout_apm.flask import ScoutApm
from wtforms import Form, TextAreaField, validators

from app.commands.bot_registration import BotRegistration
from app.commands.challenges_registration import ChallengesRegistration
from app.common.constants_and_variables import AppVariables
from app.common.execution_time import execution_time
from app.resources.strava_telegram_webhooks import StravaTelegramWebhooksResource

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.os.environ.get('LOGGING_LEVEL'))
logger = logging.getLogger(__name__)

app_variables = AppVariables()
strava_telegram_webhooks = StravaTelegramWebhooksResource()
bot_registration = BotRegistration()
challenges_registration = ChallengesRegistration()

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
    return "Welcome. Visit /register to register."


@app.route("/register")
def register():
    strava_auth_url = app_variables.strava_auth_url.format(client_id=app_variables.client_id,
                                                           redirect_uri=app_variables.redirect_uri)
    return redirect(strava_auth_url, code=302)


@app.route("/auth")
def auth_callback():
    code = request.args.get('code')
    return redirect(url_for('registration', code=code))


@app.route("/registration/<code>", methods=['GET', 'POST'])
@execution_time
def registration(code):
    try:
        form = ReusableForm(request.form)
        if request.method == 'POST':
            telegram_username = request.form['telegram_username'].strip()
            if form.validate():
                logging.info(
                    "Registering Telegram user: {telegram_username}..".format(telegram_username=telegram_username))
                if bot_registration.main(telegram_username, code):
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
        message = "Something went wrong. Exception: {exception}".format(exception=traceback.format_exc())
        logging.error(message)
        strava_telegram_webhooks.shadow_message(message)


@app.route("/challenges/even/register")
def challenges_even_register():
    strava_auth_url = app_variables.strava_challenges_auth_url.format(client_id=app_variables.challenges_client_id,
                                                                      redirect_uri=app_variables.challenges_even_redirect_uri)
    return redirect(strava_auth_url, code=302)


@app.route("/challenges/odd/register")
def challenges_odd_register():
    strava_auth_url = app_variables.strava_challenges_auth_url.format(client_id=app_variables.challenges_client_id,
                                                                      redirect_uri=app_variables.challenges_odd_redirect_uri)
    return redirect(strava_auth_url, code=302)


@app.route("/challenges/even/auth")
def challenges_even_auth():
    code = request.args.get('code')
    return redirect(url_for('challenges_registration_month_code', month="even", code=code))


@app.route("/challenges/odd/auth")
def challenges_odd_auth():
    code = request.args.get('code')
    return redirect(url_for('challenges_registration_month_code', month="odd", code=code))


@app.route("/challenges/registration/<month>/<code>")
@execution_time
def challenges_registration_month_code(month, code):
    if challenges_registration.main(month, code):
        return render_template('challenges_registration_successful.html', page_title=app_variables.page_title)
    else:
        return render_template('failed.html', page_title=app_variables.page_title)


if __name__ == '__main__' and __package__ is None:
    app.run(host=app_variables.app_host, port=app_variables.app_port, debug=app_variables.app_debug)
