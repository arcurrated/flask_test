from app import db, lm, app
from hashlib import md5

#db role constants
ROLE_USER = 0
ROLE_ADMIN = 1

@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

followers = db.Table('followers', 
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64))
	login = db.Column(db.String(64), index = True, unique = True)
	password = db.Column(db.String(64))
	role = db.Column(db.SmallInteger, default=ROLE_USER)
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime)
	followed = db.relationship('User', secondary=followers,
		primaryjoin = (followers.c.follower_id == id),
		secondaryjoin = (followers.c.followed_id == id),
		backref = db.backref('followers', lazy='dynamic'),
		lazy='dynamic')

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return str(self.id)

	def get_avatar(self, size):
		return 'http://www.gravatar.com/avatar/{}?d=mm&s={}'.format(md5(self.login.encode('utf-8')).hexdigest(), str(size))

	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)
			return self

	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)
			return self

	def is_following(self, user):
		return self.followed.filter(followers.c.followed_id==user.id).count() > 0

	def followed_posts(self):
		return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id==self.id).order_by(Post.timestamp.desc())

	def __repr__(self):
		return '<User {} with login {}>'.format(self.name, self.login)

class Post(db.Model):
	__searchable__ = ['body']

	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post {}>'.format(self.body) 
