#  -*- encoding: utf-8 -*-

import logging
import traceback

from flask import Flask, request, redirect, render_template, url_for, flash
from scout_apm.flask import ScoutApm
from wtforms import Form, TextAreaField, validators, RadioField, StringField, SelectField

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


class RegistrationBot(Form):
    telegram_username = TextAreaField('Telegram Username:', validators=[validators.required()])


class RegistrationFormBoschEven(Form):
    challenge_one = RadioField('Challenge 1:', validators=[validators.DataRequired()],
                               choices=[('CycleToWork', 'CycleToWork')], default='CycleToWork')
    challenge_two = RadioField('Challenge 2:', validators=[validators.DataRequired()],
                               choices=[('6x15', '6x15'), ('30x30', '30x30'), ('distance', 'How far can you go')])
    ntid = StringField('NTID:', validators=[validators.DataRequired()])
    email = StringField('Official Email ID:', validators=[validators.DataRequired()])
    phone = StringField('Phone Number:', validators=[validators.DataRequired()])
    location = SelectField('Location:', validators=[validators.DataRequired()],
                           choices=[("", "---"), ('EC', 'EC'), ('KOR', 'KOR'), ('BMH', 'BMH'), ('GTP', 'GTP'),
                                    ('Audugodi', 'Audugodi'),
                                    ('MRH', 'MRH'), ('Bellandur', 'Bellandur'), ('COB', 'COB'), ('Hyd', 'Hyd'),
                                    ('Others', 'Others')])


class RegistrationFormCadence90Odd(Form):
    utr = StringField('UTR / Bank Reference No.:', validators=[validators.DataRequired()])
    email = StringField('Email ID:', validators=[validators.DataRequired()])
    phone = StringField('Phone Number:', validators=[validators.DataRequired()])


REGISTRATION = {
    "cadence90": {
        "odd": {
            "page_title": app_variables.challenges_odd_page_title,
            "form": RegistrationFormCadence90Odd,
            "registration": "challenges_cadence90_odd_registration.html"
        },
        "even": {
            "page_title": app_variables.challenges_even_page_title,
            "form": "",
            "registration": "challenges_cadence90_even_registration.html"
        }
    },
    "bosch": {
        "odd": {
            "page_title": app_variables.challenges_bosch_odd_page_title,
            "form": "",
            "registration": "challenges_bosch_odd_registration.html"
        },
        "even": {
            "page_title": app_variables.challenges_bosch_even_page_title,
            "form": RegistrationFormBoschEven,
            "registration": "challenges_bosch_even_registration.html"
        }
    },
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
                if bot_registration.main(telegram_username, code, "bot"):
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
        strava_telegram_webhooks.send_message(message)


@app.route("/register/challenges/<company>/<month>")
def challenges_register(company, month):
    logging.info("Register - Company: %s | Month: %s", company, month)
    if company in REGISTRATION and month in REGISTRATION[company]:
        redirect_uri = app_variables.challenges_redirect_uri.format(app_host=app_variables.app_host, company=company,
                                                                    month=month)
        strava_auth_url = app_variables.strava_challenges_auth_url.format(client_id=app_variables.challenges_client_id,
                                                                          redirect_uri=redirect_uri,
                                                                          scope=app_variables.strava_challenges_auth_scope)
        return redirect(strava_auth_url, code=302)


@app.route("/auth/challenges/<company>/<month>")
def challenges_auth(company, month):
    logging.info("Auth - Company: %s | Month: %s", company, month)
    code = request.args.get('code')
    permissions = request.args.get('scope')
    if permissions != app_variables.strava_challenges_auth_scope:
        page_title = REGISTRATION[company][month]['page_title']
        redirect_uri = app_variables.challenges_redirect_uri.format(app_host=app_variables.app_host, company=company,
                                                                    month=month)
        strava_auth_url = app_variables.strava_challenges_auth_url.format(client_id=app_variables.challenges_client_id,
                                                                          redirect_uri=redirect_uri,
                                                                          scope=app_variables.strava_challenges_auth_scope)
        strava_telegram_webhooks.send_message(
            "Insufficient permissions for {company} {month} challenge.".format(company=company, month=month))
        return render_template('failed_permissions.html', page_title=page_title, auth_link=strava_auth_url)
    else:
        return redirect(url_for('challenges_registration', company=company, month=month, code=code))


@app.route("/registration/challenges/<company>/<month>/<code>", methods=['GET', 'POST'])
@execution_time
def register_for_challenges(company, month, code):
    logging.info("Registration - Company: %s | Month: %s", company, month)
    form = REGISTRATION[company][month]['form'](request.form)
    page_title = REGISTRATION[company][month]['page_title']
    if request.method == 'POST':
        if form.validate():
            if challenges_registration.main(company, month, code, form):
                return render_template('challenges_registration_successful.html', page_title=page_title)
            else:
                return render_template('failed.html', page_title=page_title)
        else:
            flash("Select / Fill appropriate fields.")

    challenges_registration_page = REGISTRATION[company][month]['registration']
    return render_template(challenges_registration_page, form=form, page_title=page_title)


if __name__ == '__main__' and __package__ is None:
    app.run(host=app_variables.app_host, port=app_variables.app_port, debug=app_variables.app_debug)
