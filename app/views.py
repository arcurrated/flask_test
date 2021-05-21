from app import app
from flask import render_template, flash, redirect
from app.forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
	user = {'name': 'Albert'}
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
	form = LoginForm()
	if form.validate_on_submit():
		flash('login req for {}, {}, remember: {}'.format(form.login.data, form.password.data, form.remember_me.data))
		return redirect('/')
	return render_template('login.html', title='Sign In', form = form)
