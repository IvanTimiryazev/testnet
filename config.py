import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()


class Config(object):
    DEBUG = 1
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    ADMINS = os.getenv('ADMINS')
    TIME_INTERVAL = 30
    REDIS_URL = os.getenv('REDIS_URL') or 'redis://'
