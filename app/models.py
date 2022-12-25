import re
import jwt
from time import time
import redis
import rq
from flask_login import UserMixin
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
import time
from datetime import datetime

from app import db, login


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), index=True, unique=True)
    password_hash = db.Column(db.String(200))
    image_file = db.Column(db.String(100), nullable=False, default='default.jpg')
    accounts = db.relationship('Source', backref='author', lazy='dynamic')
    regs = db.relationship('UsersRegex', backref='author', lazy='dynamic')
    tasks = db.relationship('Task', backref='user', lazy='dynamic')
    results = db.relationship('LastParseResults', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User: {self.username}, Email: {self.email}>'

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    def user_tweeter_accounts(self):
        s = [i for i in Source.query.filter_by(user_id=self.id).order_by(Source.created.desc())]
        return s

    def user_regs(self):
        regs = [i for i in UsersRegex.query.filter_by(user_id=self.id).order_by(UsersRegex.created.desc())]
        return regs

    def user_tweeter_accounts_for_p(self):
        s = [i.account for i in Source.query.filter_by(user_id=self.id).order_by(Source.created.desc())]
        accounts = [re.sub(r',|@', '', a) for a in s]
        print(accounts)
        return accounts

    def user_regs_for_p(self):
        regs = [
            i.regex.lower() for i in UsersRegex.query.filter_by(user_id=self.id).order_by(UsersRegex.created.desc())
        ]
        return regs

    def remove_tweeter_account(self, id):
        self.accounts.filter_by(id=id).delete()

    def remove_users_regex(self, id):
        self.regs.filter_by(id=id).delete()

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password.txt': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    def save_parse_results(self, results):
        if LastParseResults.query.filter_by(user_id=self.id).all():
            LastParseResults.query.filter_by(user_id=self.id).delete()
        for i in results:
            result = LastParseResults(
                url=i['url'], content=i['content'], date=i['date'], user=self)
            db.session.add(result)
        db.session.commit()

    def get_parse_results(self):
        results = [
            {
                'url': i.url, 'content': i.content, 'date': i.date
            } for i in LastParseResults.query.filter_by(user_id=self.id).order_by(LastParseResults.date.desc())
        ]
        return results

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token, current_app.config['SECRET_KEY'],
                algorithms=['HS256'])['reset_password.txt']
        except:
            return
        return Users.query.get(id)

    def launch_tasks(self, name, description, *args, **kwargs):
        job = current_app.task_queue.enqueue(
            'app.parse.' + name, self.user_tweeter_accounts_for_p(),
            self.user_regs_for_p(), *args, **kwargs)
        task = Task(id=job.get_id(), name=name, description=description, user=self)
        db.session.add(task)
        db.session.commit()
        while not job.is_finished:
            time.sleep(2)
        print(job.result)
        if len(job.result) > 0:
            self.save_parse_results(job.result)
        return job.result

    def get_tasks_in_progress(self):
        return self.tasks.filter_by(complete=False).all()

    def get_task_in_progress(self, name):
        return self.tasks.filter_by(name=name, complete=False).first()


class Source(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(250))
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Acc: {self.account}>'


class UsersRegex(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    regex = db.Column(db.String(100))
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Regex: {self.regex}>'


class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    complete = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Name: {self.name}, status: {self.complete}>'

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100


class LastParseResults(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(100))
    content = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<url: {self.url}>'


@login.user_loader
def load_user(id: str):
    return Users.query.get(int(id))
