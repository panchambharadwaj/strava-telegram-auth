from wtforms import Form, TextAreaField, validators


class RegistrationBot(Form):
    telegram_username = TextAreaField('Telegram Username:', validators=[validators.input_required()])
