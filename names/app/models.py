from app import db
from flask.ext.login import AnonymousUserMixin
from flask import request


# TODO: Eliminate the interface because it didn't end up working
# TODO: Implement togglable profile privacy


class IUser(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    flags = db.Column(db.Integer)
    ip = db.Column(db.String(32))
    is_active = db.Column(db.Boolean)
    is_authenticated = db.Column(db.Boolean)
    is_anonymous = db.Column(db.Boolean)

    def __init__(self):
        self.flags = 0

    def get_id(self):
        return self.id


class User(IUser, db.Model):
    username = db.Column(db.String(32))
    password = db.Column(db.String(128))
    photo_url = db.Column(db.String(128))
    suggestions = db.Column(db.Boolean)
    about = db.Column(db.String(1024))  # for gender, age, what type of name sought, any misc. info

    def __init__(self, name, password, url, about):
        super().__init__()
        self.username = name
        self.password = password
        self.photo_url = url
        self.about = about
        self.suggestions = True

        self.is_active = True
        self.is_authenticated = True
        self.is_anonymous = False

    def __repr__(self):
        return "<User %r>" % self.name


class Anon(AnonymousUserMixin):

    def __init__(self):
        super().__init__()
        self.ip = request.remote_addr

    def __repr__(self):
        return "<Anon %r>" % self.ip


class Name(db.Model):
    __tablename__ = 'name'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    score = db.Column(db.Integer)

    userID = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', foreign_keys=[userID])
    suggesterID = db.Column(db.Integer, db.ForeignKey('user.id'))
    suggester = db.relationship('User', foreign_keys=[suggesterID])

    def __init__(self, name, user, suggester):
        self.name = name
        self.user = user
        self.score = 0
        self.suggester = suggester

    def __repr__(self):
        return "<Name %r>" % self.name


class Vote(db.Model):
    __tablename__ = 'vote'
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'))
    nameID = db.Column(db.Integer, db.ForeignKey('name.id'))
    user = db.relationship('User', foreign_keys=[userID])
    name = db.relationship('Name', foreign_keys=[nameID])
    voterID = db.Column(db.Integer, db.ForeignKey('user.id'))
    voter = db.relationship('User', foreign_keys=[voterID])

    def __init__(self, name, user, voter):
        self.name = name
        self.user = user
        self.voter = voter

    def __repr__(self):
        return "<Vote %r>" % self.id


db.create_all()
db.session.commit()
