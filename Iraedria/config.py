import os
from enum import Enum

WTF_CSRF_ENABLED = True
# SECRET_KEY = "i have been working on this novel for ten and a half years"

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_TRACK_MODIFICATIONS = True

PATH_TO_BASE_TEMPLATE = os.path.join(basedir, 'templates/base.html')
PATH_TO_NOVEL = os.path.join(basedir, 'static/text')


class Book(Enum):
    vega = 1
    gardena = 2
    home = 3
    siege = 4

