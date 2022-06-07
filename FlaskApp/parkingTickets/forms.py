from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, DateField
from wtforms.validators import DataRequired
from parkingTickets.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class SearchBySummonsForm(FlaskForm):
    summons_num = IntegerField('summons_num', validators=[DataRequired()])
    submit = SubmitField('Search')


class SearchByPlateForm(FlaskForm):
    plate = StringField('plate', validators=[DataRequired()])
    submit = SubmitField('Search')


class SearchByDateForm(FlaskForm):
    start_date = DateField('start_date', validators=[DataRequired()])
    end_date = DateField('end_date', validators=[DataRequired()])
    submit = SubmitField('Search')
