#  -*- encoding: utf-8 -*-


import logging
import traceback

import psycopg2
import requests
from app.common.constants_and_variables import AppVariables, AppConstants
from flask import Flask, request, redirect, render_template, url_for, flash
from wtforms import Form, TextAreaField, validators

app_variables = AppVariables()
app_constants = AppConstants()

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = app_variables.secret_key


class ReusableForm(Form):
    telegram_username = TextAreaField('Telegram Username:', validators=[validators.required()])


def token_exchange(code):
    response = requests.post(app_constants.API_TOKEN_EXCHANGE, data={
        'client_id': int(app_variables.client_id),
        'client_secret': app_variables.client_secret,
        'code': code,
        'grant_type': 'authorization_code'
    }).json()

    access_info = dict()

    access_info['athlete_id'] = response['athlete']['id']
    access_info['access_token'] = response['access_token']
    access_info['refresh_token'] = response['refresh_token']
    access_info['expires_at'] = response['expires_at']

    return access_info


def athlete_exists(athlete_id):
    database_connection = psycopg2.connect(app_variables.database_url, sslmode='require')
    cursor = database_connection.cursor()
    cursor.execute(app_constants.QUERY_ATHLETE_EXISTS.format(athlete_id=athlete_id))
    count = cursor.fetchone()[0]
    cursor.close()
    database_connection.close()

    return True if count > 0 else False


def add_or_update_into_table(query, access_info, telegram_username):
    database_connection = psycopg2.connect(app_variables.database_url, sslmode='require')
    cursor = database_connection.cursor()
    cursor.execute(query.format(
        athlete_id=access_info['athlete_id'],
        access_token=access_info['access_token'],
        refresh_token=access_info['refresh_token'],
        expires_at=access_info['expires_at'],
        telegram_username=telegram_username))
    cursor.close()
    database_connection.commit()
    database_connection.close()


@app.route("/")
def home():
    return "Welcome. Visit /register to register."


@app.route("/register")
def register():
    return redirect(app_variables.strava_auth_url.format(client_id=app_variables.client_id,
                                                         redirect_uri=app_variables.redirect_uri), code=302)


@app.route("/auth")
def auth_callback():
    code = request.args.get('code')
    return redirect(url_for('registration', code=code))


@app.route("/registration/<code>", methods=['GET', 'POST'])
def registration(code):
    form = ReusableForm(request.form)
    if request.method == 'POST':
        telegram_username = request.form['telegram_username'].strip()

        if form.validate():
            try:
                access_info = token_exchange(code)
                if not athlete_exists(access_info['athlete_id']):
                    query = app_constants.QUERY_INSERT_VALUES
                    add_or_update_into_table(query, access_info, telegram_username)
                    logging.info("Added new athlete {athlete_id}".format(athlete_id=access_info['athlete_id']))
                else:
                    query = app_constants.QUERY_UPDATE_VALUES
                    add_or_update_into_table(query, access_info, telegram_username)
                    logging.info("Updated athlete {athlete_id}".format(athlete_id=access_info['athlete_id']))

                return render_template('successful.html', page_title=app_variables.page_title)

            except Exception:
                logging.exception("Exception: {exception_traceback}".format(exception_traceback=traceback.format_exc()))
                return render_template('failed.html', page_title=app_variables.page_title)
        else:
            flash('Telegram Username is Mandatory', 'Error')

    return render_template('registration.html', form=form, page_title=app_variables.page_title)


if __name__ == '__main__' and __package__ is None:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)
    app.run(host=app_variables.app_host, port=app_variables.app_port, debug=app_variables.app_debug)
