import os
import unittest

from config import basedir
from app import app,db
from app.models import User

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

if __name__ == '__main__':
	unittest.main()