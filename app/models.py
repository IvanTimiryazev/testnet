import re
from app import db, login
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


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
        accounts = []
        for j in s:
            j = j.split()
            for k in j:
                res = re.sub(r',|@', '', k)
                accounts.append(res)
        return accounts


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
