from wtforms import Form, TextAreaField, validators, RadioField, StringField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Length


class RegistrationBot(Form):
    telegram_username = TextAreaField('Telegram Username:', validators=[validators.required()])


class RegistrationFormCadence90Odd(Form):
    utr = StringField('UTR / Bank Reference No.:', validators=[validators.DataRequired()])
    phone = StringField('Phone Number:', validators=[validators.DataRequired(), Length(min=6, max=15)])
    email = EmailField('Email ID:', validators=[validators.DataRequired(), validators.Email()])


class RegistrationFormCadence90Even(Form):
    utr = StringField('UTR / Bank Reference No.:', validators=[validators.DataRequired()])
    phone = StringField('Phone Number:', validators=[validators.DataRequired(), Length(min=6, max=15)])
    email = EmailField('Email ID:', validators=[validators.DataRequired(), validators.Email()])


class RegistrationFormBoschOdd(Form):
    challenge_one = RadioField('Challenge 1:', validators=[validators.DataRequired()],
                               choices=[('c2w_rides', 'CycleToWork Rides'), ('c2w_distance', 'CycleToWork Distance')])
    challenge_two = RadioField('Challenge 2:', validators=[validators.DataRequired()],
                               choices=[('2x30', '2km x 30 (only for Woman riders)'), ('40x30', '40min x 30rides'),
                                        ('distance', 'How far can you go')])
    ntid = StringField('NTID:', validators=[validators.DataRequired()])
    email = StringField('Official Email ID:', validators=[validators.DataRequired(), validators.Email()])
    phone = StringField('Phone Number:', validators=[validators.DataRequired(), Length(min=6, max=15)])
    location = SelectField('Location:', validators=[validators.DataRequired()],
                           choices=[("", "---"), ('EC', 'EC'), ('KOR', 'KOR'), ('BMH', 'BMH'), ('GTP', 'GTP'),
                                    ('Audugodi', 'Audugodi'),
                                    ('MRH', 'MRH'), ('Bellandur', 'Bellandur'), ('COB', 'COB'), ('Hyd', 'Hyd'),
                                    ('OM', 'OM'), ('Others', 'Others')])


class RegistrationFormBoschEven(Form):
    challenge_one = RadioField('Challenge 1:', validators=[validators.DataRequired()],
                               choices=[('c2w_rides', 'CycleToWork Rides'), ('c2w_distance', 'CycleToWork Distance')])
    challenge_two = RadioField('Challenge 2:', validators=[validators.DataRequired()],
                               choices=[('2x30', '2km x 30 (only for Woman riders)'), ('40x30', '40min x 30rides'),
                                        ('distance', 'How far can you go')])
    ntid = StringField('NTID:', validators=[validators.DataRequired()])
    email = StringField('Official Email ID:', validators=[validators.DataRequired(), validators.Email()])
    phone = StringField('Phone Number:', validators=[validators.DataRequired(), Length(min=6, max=15)])
    location = SelectField('Location:', validators=[validators.DataRequired()],
                           choices=[("", "---"), ('EC', 'EC'), ('KOR', 'KOR'), ('BMH', 'BMH'), ('GTP', 'GTP'),
                                    ('Audugodi', 'Audugodi'),
                                    ('MRH', 'MRH'), ('Bellandur', 'Bellandur'), ('COB', 'COB'), ('Hyd', 'Hyd'),
                                    ('OM', 'OM'), ('Others', 'Others')])
