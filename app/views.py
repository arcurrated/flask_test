from app import app, db, lm
from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm
from app.models import User, ROLE_USER, ROLE_ADMIN

@app.before_request
def before_request():
	g.user = current_user

@app.route('/')
@app.route('/index')
@login_required
def index():
	user = g.user
	data = [
		{
			'id': 13,
			'unit': '1 AVTR',
			'fio' : 'Bashir',
		}, 
		{
			'id': 14,
			'unit': '2 AVTR',
			'fio': 'Restey',
		}
	]
	# return
	return render_template("index.html", title='Home', user=user, data=data)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if g.user is not None and g.user.is_authenticated:
			return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		_login = form.login.data
		_password = form.password.data
		user = User.query.filter_by(login=_login, password=_password).first()
		if user is None:
			flash('Invalid login or pass')
			return redirect(url_for('login'))
		remember_me = form.remember_me.data
		login_user(user, remember=remember_me)
		return redirect(request.args.get('next') or url_for('index'))
	return render_template('login.html', title='Sign In', form = form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))
