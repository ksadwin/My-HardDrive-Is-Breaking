from app import db
from flask_login import AnonymousUserMixin
from flask import request, url_for


# TODO: Implement togglable profile privacy


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    flags = db.Column(db.Integer)
    ip = db.Column(db.String(32))
    active = db.Column(db.Boolean)
    authenticated = db.Column(db.Boolean)
    anonymous = db.Column(db.Boolean)

    username = db.Column(db.String(32))
    password = db.Column(db.String(128))
    photo_url = db.Column(db.String(128))
    suggestions = db.Column(db.Boolean)
    about = db.Column(db.String(1024))  # for gender, age, what type of name sought, any misc. info
    private = db.Column(db.Boolean)

    def __init__(self, name, password, url, about):
        self.flags = 0
        self.username = name
        self.password = password

        no_photo = False
        if url == "":  # no photo given. FIXME: check photo validity here. alternatively: do a cool JS thing
            self.photo_url = url_for('static', filename='default.jpg')
            no_photo = True
        else:  # photo given
            self.photo_url = url

        if about == "" and no_photo:  # no photo or description provided
            self.about = "This user isn't giving you much to work with. Well, do your best."
        elif about == "":  # there is a photo but no description
            self.about = "This user thinks a picture is worth a thousand words."
        else:  # everything is normal
            self.about = about

        self.suggestions = True

        self.active = True
        self.authenticated = True
        self.anonymous = False
        self.private = False

    def is_active(self):
        return self.active

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return self.anonymous

    def get_id(self):
        return self.id

    def __repr__(self):
        return "<User %r>" % self.username


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
