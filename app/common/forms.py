from wtforms import Form, TextAreaField, validators, RadioField, StringField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Length


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
    phone = StringField('Phone Number:', validators=[validators.DataRequired(), Length(min=6, max=15)])
    email = EmailField('Email ID:', validators=[validators.DataRequired(), validators.Email()])
