#  -*- encoding: utf-8 -*-

import logging
import traceback

from flask import Flask, request, redirect, render_template, url_for, flash
from scout_apm.flask import ScoutApm

from app.commands.challenges_registration import ChallengesRegistration
from app.common.constants_and_variables import AppVariables
from app.common.execution_time import execution_time
from app.common.forms import RegistrationBot, RegistrationFormBoschEven, RegistrationFormCadence90Odd, \
    RegistrationFormBoschOdd, RegistrationFormCadence90Even, RegistrationFormTokOdd, RegistrationFormTokEven
from app.resources.strava_telegram_webhooks import StravaTelegramWebhooksResource

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.os.environ.get('LOGGING_LEVEL'))
logger = logging.getLogger(__name__)

app_variables = AppVariables()
strava_telegram_webhooks = StravaTelegramWebhooksResource()
challenges_registration = ChallengesRegistration()

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = app_variables.secret_key

ScoutApm(app)

app.config['SCOUT_MONITOR'] = app_variables.scout_monitor
app.config['SCOUT_KEY'] = app_variables.scout_key
app.config['SCOUT_NAME'] = app_variables.scout_name


CHALLENGES_REGISTRATION = {
    "cadence90": {
        "odd": {
            "page_title": app_variables.challenges_odd_page_title,
            "form": RegistrationFormCadence90Odd,
            "registration": "challenges_cadence90_odd_registration.html",
            "registration_confirmation": "challenges_cadence90_odd_registration_successful.html"
        },
        "even": {
            "page_title": app_variables.challenges_even_page_title,
            "form": RegistrationFormCadence90Even,
            "registration": "challenges_cadence90_even_registration.html",
            "registration_confirmation": "challenges_cadence90_even_registration_successful.html"
        }
    },
    "bosch": {
        "odd": {
            "page_title": app_variables.challenges_bosch_odd_page_title,
            "form": RegistrationFormBoschOdd,
            "registration": "challenges_bosch_odd_registration.html",
            "registration_confirmation": "challenges_registration_successful.html"
        },
        "even": {
            "page_title": app_variables.challenges_bosch_even_page_title,
            "form": RegistrationFormBoschEven,
            "registration": "challenges_bosch_even_registration.html",
            "registration_confirmation": "challenges_registration_successful.html"
        }
    },
    "tok": {
        "odd": {
            "page_title": app_variables.challenges_tok_odd_page_title,
            "form": RegistrationFormTokOdd,
            "registration": "challenges_tok_odd_registration.html",
            "registration_confirmation": "challenges_tok_odd_registration_successful.html"
        },
        "even": {
            "page_title": app_variables.challenges_tok_even_page_title,
            "form": RegistrationFormTokEven,
            "registration": "challenges_tok_even_registration.html",
            "registration_confirmation": "challenges_tok_even_registration_successful.html"
        }
    }
}


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
        strava_telegram_webhooks.send_message("Insufficient permissions.")
        return render_template('failed_permissions.html', page_title=page_title, auth_link=strava_auth_url)
    else:
        return redirect(url_for('registration', code=code))


@app.route("/registration/<code>", methods=['GET', 'POST'])
@execution_time
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


# @app.route("/register/challenges/<company>/<month>")
# def challenges_register_redirect(company, month):
#     logging.info("Register - Company: %s | Month: %s", company, month)
#     if company in CHALLENGES_REGISTRATION and month in CHALLENGES_REGISTRATION[company]:
#         redirect_uri = app_variables.challenges_redirect_uri.format(app_host=app_variables.app_host, company=company,
#                                                                     month=month)
#         strava_auth_url = app_variables.strava_challenges_auth_url.format(client_id=app_variables.challenges_client_id,
#                                                                           redirect_uri=redirect_uri,
#                                                                           scope=app_variables.strava_challenges_auth_scope)
#         return redirect(strava_auth_url, code=302)
#
#
# @app.route("/auth/challenges/<company>/<month>")
# def challenges_auth(company, month):
#     logging.info("Auth - Company: %s | Month: %s", company, month)
#     code = request.args.get('code')
#     permissions = request.args.get('scope')
#     if permissions != app_variables.strava_challenges_auth_scope:
#         page_title = CHALLENGES_REGISTRATION[company][month]['page_title']
#         redirect_uri = app_variables.challenges_redirect_uri.format(app_host=app_variables.app_host, company=company,
#                                                                     month=month)
#         strava_auth_url = app_variables.strava_challenges_auth_url.format(client_id=app_variables.challenges_client_id,
#                                                                           redirect_uri=redirect_uri,
#                                                                           scope=app_variables.strava_challenges_auth_scope)
#         strava_telegram_webhooks.send_message(
#             "Insufficient permissions for {company} {month} challenge.".format(company=company, month=month))
#         return render_template('failed_permissions.html', page_title=page_title, auth_link=strava_auth_url)
#     else:
#         return redirect(url_for('challenges_register', company=company, month=month, code=code))


# @app.route("/registration/challenges/<company>/<month>/<code>", methods=['GET', 'POST'])
# @execution_time
# def challenges_register(company, month, code):
#     logging.info("Registration - Company: %s | Month: %s", company, month)
#     form = CHALLENGES_REGISTRATION[company][month]['form'](request.form)
#     page_title = CHALLENGES_REGISTRATION[company][month]['page_title']
#     if request.method == 'POST':
#         if form.validate():
#             if challenges_registration.main(company, month, code, form):
#                 return render_template(CHALLENGES_REGISTRATION[company][month]['registration_confirmation'],
#                                        page_title=page_title)
#             else:
#                 return render_template('failed.html', page_title=page_title)
#
#     challenges_registration_page = CHALLENGES_REGISTRATION[company][month]['registration']
#     return render_template(challenges_registration_page, form=form, page_title=page_title)


if __name__ == '__main__' and __package__ is None:
    app.run(host=app_variables.app_host, port=app_variables.app_port, debug=app_variables.app_debug)
