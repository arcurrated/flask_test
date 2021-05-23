import os
import unittest
from datetime import datetime, timedelta

from config import basedir
from app import app,db
from app.models import User, Post

class TestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['CSRF_ENABLED'] = False
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(os.path.join(basedir, 'test.db'))
		self.app = app.test_client()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def test_make_uniq_login(self):
		u = User(login='joe', password='123')
		db.session.add(u)
		db.session.commit()
		u = User(login='joe', password='123')
		try:
			db.session.add(u)
			db.session.commit()
			assert False
		except:
			assert True

	def test_follow(self):
		u1 = User(login='joe', password='123')
		u2 = User(login='bar', password='123')
		db.session.add(u1)
		db.session.add(u2)
		db.session.commit()
		assert u1.unfollow(u2) == None
		u = u1.follow(u2)
		db.session.add(u)
		db.session.commit()
		assert u1.follow(u2) == None
		assert u1.is_following(u2)
		assert u1.followed.count() == 1
		assert u2.followers.count() == 1
		u = u1.unfollow(u2)
		assert u is not None
		db.session.add(u)
		db.session.commit()
		assert not u1.is_following(u2)
		assert u1.followers.count() == 0
		assert u2.followed.count() == 0

	def test_follower_posts(self):
		u1 = User(login='bar', password='123')
		u2 = User(login='foo')
		u3 = User(login='chi')
		u4 = User(login='abs')
		db.session.add_all([u1, u2, u3, u4])
		utcnow = datetime.utcnow()
		p1 = Post(body='text', author=u1, timestamp = utcnow+timedelta(seconds=1))
		p2 = Post(body='text', author=u2, timestamp = utcnow+timedelta(seconds=2))
		p3 = Post(body='text', author=u2, timestamp = utcnow+timedelta(seconds=3))
		p4 = Post(body='text', author=u4, timestamp = utcnow+timedelta(seconds=4))
		db.session.add_all([p1, p2, p3, p4])
		db.session.commit()
		u1.follow(u1)
		u2.follow(u2)
		u3.follow(u3)
		u4.follow(u4)
		u2.follow(u1)
		u3.follow(u4)
		u3.follow(u1)
		db.session.add_all([u1, u2, u3, u4])
		f1 = u1.followed_posts().all()
		f2 = u2.followed_posts().all()
		f3 = u3.followed_posts().all()
		f4 = u4.followed_posts().all()
		assert len(f1) == 1
		assert len(f2) == 3
		assert len(f3) == 2
		assert len(f4) == 1
		assert f1 == [p1,]
		assert f2 == [p3, p2, p1]
		assert f3 == [p4, p1]
		assert f4 == [p4]

if __name__ == '__main__':
	unittest.main()