from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, BooleanField
from wtforms.validators import Required

class LoginForm(FlaskForm):
	login = TextField('login', validators=[Required()])
	password = PasswordField('pass')
	remember_me = BooleanField('remember_me', default=False)
