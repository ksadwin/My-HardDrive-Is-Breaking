from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_admin import Admin

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.config.from_object('config')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
bootstrap = Bootstrap(app)
admin = Admin(app, name='NameChangerDB', template_mode='bootstrap3')


# must go at end of file to avoid import loop
from app import views, models

