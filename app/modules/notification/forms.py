from flask_wtf import FlaskForm
from wtforms import SubmitField


class NotificationForm(FlaskForm):
    submit = SubmitField('Save notification')
