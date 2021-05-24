from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import Required, EqualTo, ValidationError, Length
from app.models import User

class LoginForm(FlaskForm):
	login = TextField('login', validators=[Required()])
	password = PasswordField('pass')
	remember_me = BooleanField('remember_me', default=False)

class RegisterForm(FlaskForm):
	name = TextField('name', validators=[Required()])
	login = TextField('login', validators=[Required()])
	password = PasswordField('pass', validators=[Required(), EqualTo('repeat_password', 'Passwords is not equal')])
	repeat_password = PasswordField('repeat_pass', validators=[Required()])

	def validate_login(form, field):
		if User.query.filter_by(login=field.data).first():
			raise ValidationError('Login already used')

class EditProfileForm(FlaskForm):
	name = TextField('name', validators=[Required()])
	about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

class PostForm(FlaskForm):
	post = TextField('post', validators=[Required()])