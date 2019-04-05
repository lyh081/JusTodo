from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(1,70)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login in')


class ItemForm(FlaskForm):
    body = StringField('Todo', validators=[DataRequired()])
    submit = SubmitField('OK')
