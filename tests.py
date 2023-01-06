import unittest

from app import create_app, db
from app.models import Users, Source
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hash(self):
        u = Users(email='lol@m.ru')
        u.set_password('man')
        self.assertFalse(u.check_password('woman'))
        self.assertTrue(u.check_password('man'))

    def test_user(self):
        u = Users(email='lol@m.ru')
        s = Source(account='@Gachi')
        s2 = Source(account='@Gucci')
        db.session.add(u)
        db.session.add(s)
        db.session.add(s2)
        self.assertEqual(u.user_tweeter_accounts(), ['Gucci', 'Gachi'])

    def test_reset_passw(self):
        u = Users(email='lol@m.ru')
        db.session.add(u)
        db.session.commit()
        token = u.get_reset_password_token()
        self.assertEqual(u.verify_reset_password_token(token), u)


if __name__ == '__main__':
    unittest.main(verbosity=2)