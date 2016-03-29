from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

app = Flask(__name__, template_folder="../templates")
app.config.from_object('config')
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

# must go at end of file to avoid import loop
from app import views, models

