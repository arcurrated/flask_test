from app import db, lm

#db role constants
ROLE_USER = 0
ROLE_ADMIN = 1

@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64))
	login = db.Column(db.String(64), index = True, unique = True)
	password = db.Column(db.String(64))
	role = db.Column(db.SmallInteger, default=ROLE_USER)
	posts = db.relationship('Post', backref='author', lazy='dynamic')

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return str(self.id)

	def __repr__(self):
		return '<User {} with login {}>'.format(self.name, self.login)

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post {}>'.format(self.body) 
