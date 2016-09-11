import os

WTF_CSRF_ENABLED = True
SECRET_KEY = "imtransx-7tszddglwiq#=shrht44@(lm6j@()9jy6*@gp+g_q+0*kl9m"

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_TRACK_MODIFICATIONS = True


