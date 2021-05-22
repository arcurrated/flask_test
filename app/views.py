from app import app, db, lm
from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm, RegisterForm, EditProfileForm
from app.models import User, ROLE_USER, ROLE_ADMIN
from datetime import datetime

@app.before_request
def before_request():
	g.user = current_user
	if g.user.is_authenticated:
		g.user.last_seen = datetime.utcnow()
		db.session.add(g.user)
		db.session.commit()

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

@app.route('/register', methods=['GET', 'POST'])
def register():
	if g.user is not None and g.user.is_authenticated:
		return redirect(url_for('logout'))
	form = RegisterForm()
	if form.validate_on_submit():
		_login = form.login.data
		_password = form.password.data
		_repeat_password = form.repeat_password.data
		_name = form.name.data
		user = User(name=_name, login=_login, password=_password)
		db.session.add(user)
		db.session.commit()
		flash('Successfully registered, please log in')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route('/user/<login>')
@login_required
def user_page(login):
	user = User.query.filter_by(login=login).first()
	if user is None:
		flash('User {} not found'.format(login))
		return redirect(url_for('index'))
	posts = [{ 'author': user, 'body': 'Test post #1' },
        { 'author': user, 'body': 'Test post #2' }]
	return render_template('user_page.html', user=user, posts=posts)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
	form = EditProfileForm()
	if form.validate_on_submit():
		g.user.nickname = form.name.data
		g.user.about_me = form.about_me.data
		db.session.add(g.user)
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('edit'))
	else:
		form.name.data = g.user.name
		form.about_me.data = g.user.about_me
	return render_template('edit_profile.html', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))
