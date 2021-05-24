from app import app, db, lm
from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm, RegisterForm, EditProfileForm, PostForm
from app.models import User, ROLE_USER, ROLE_ADMIN, Post
from datetime import datetime
from config import POSTS_PER_PAGE

@app.before_request
def before_request():
	g.user = current_user
	if g.user.is_authenticated:
		g.user.last_seen = datetime.utcnow()
		db.session.add(g.user)
		db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
	user = g.user
	form = PostForm()
	if form.validate_on_submit():
		post = Post(body=form.post.data, timestamp = datetime.utcnow(), author=g.user)
		db.session.add(post)
		db.session.commit()
		flash('Post done')
		return redirect(url_for('index'))

	posts = user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
	return render_template("index.html", title='Home', user=user, posts=posts, form=form)

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
		user.follow(user)
		db.session.add(user)
		db.session.commit()
		flash('Successfully registered, please log in')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route('/user/<login>')
@app.route('/user/<login>/<int:page>')
@login_required
def user_page(login, page=1):
	user = User.query.filter_by(login=login).first()
	if user is None:
		flash('User {} not found'.format(login))
		return redirect(url_for('index'))
	posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
	return render_template('user_page.html', user=user, posts=posts)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

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

@app.route('/follow/<login>')
@login_required
def follow(login):
	user = User.query.filter_by(login=login).first()
	if user is None:
		flash('User {} not found'.format(login))
		return redirect(url_for('index'))
	if user == g.user:
		flash('U can\'t follow yourself')
		return redirect(url_for(user_page, login=login))
	u = g.user.follow(user)
	if u is None:
		flash('Cannot follow {}'.format(login))
		return redirect(url_for('user_page', login=login))
	db.session.add(u)
	db.session.commit()
	flash('You are now following {}'.format(login))
	return redirect(url_for('user_page', login=login))

@app.route('/unfollow/<login>')
@login_required
def unfollow(login):
	user = User.query.filter_by(login=login).first()
	if user is None:
		flash('User {} not found'.format(login))
		return redirect(url_for('index'))
	if user == g.user:
		flash('U can\'t unfollow yourself')
		return redirect(url_for('user_page', login=login))
	u = g.user.unfollow(user)
	if u is None:
		flash('Cannot unfollow {}'.format(login))
		return redirect(url_for('user_page', login=login))
	db.session.add(u)
	db.session.commit()
	flash('U were successfully unfollowed from {}'.format(login))
	return redirect(url_for('user_page', login=login))

# errors
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500