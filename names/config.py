import os

WTF_CSRF_ENABLED = True
SECRET_KEY = "this is about as secret as the fact that i'm trans. everyone on the internet knows now"

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_TRACK_MODIFICATIONS = True


