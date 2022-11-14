import re
import jwt
from time import time
from datetime import datetime

from flask_login import UserMixin
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), index=True, unique=True)
    email = db.Column(db.String(150), index=True, unique=True)
    password_hash = db.Column(db.String(200))
    phone_number = db.Column(db.String(50))
    image_file = db.Column(db.String(100), nullable=False, default='default.jpg')
    accounts = db.relationship('Source', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<User: {self.username}, Email: {self.email}>'

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    def user_tweeter_accounts(self):
        s = [i.account for i in Source.query.filter_by(user_id=self.id).order_by(Source.created.desc())]
        accounts = [re.sub(r',|@', '', a) for a in s]
        return accounts

    def remove_tweeter_account(self):
        pass

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password.txt': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token, current_app.config['SECRET_KEY'],
                algorithms=['HS256'])['reset_password.txt']
        except:
            return
        return Users.query.get(id)


class Source(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(250))
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Acc: {self.account}>'


@login.user_loader
def load_user(id: str):
    return Users.query.get(int(id))
