from app import db
import time
from enum import Enum
import os


def get_text_from_path(fpath):
    f = open(fpath, "r")
    text = f.read()
    f.close()
    return text


class Book(Enum):
    vega = 1
    gardena = 2
    home = 3
    siege = 4


class Chapter(db.Model):
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True)
    num = db.Column(db.Integer)
    text = db.Column(db.String)  # gave it no length parameter, let's see what happens?
    date_added = db.Column(db.Integer)
    date_modified = db.Column(db.Integer)
    booknum = db.Column(db.Integer)
    likes = db.Column(db.Integer)
    photo_url = db.Column(db.String)  # comma-separated list of urls
    visible = db.Column(db.Boolean)

    def __init__(self, filename, bookstr):
        bookstr = bookstr.lower()
        self.booknum = Book[bookstr].value
        self.num = os.path.splitext(os.path.basename(filename))[0]

        self.date_added = time.time()
        self.date_modified = os.path.getmtime(filename)

        self.text = get_text_from_path(filename)

        self.likes = 0
        self.visible = True

    def __repr__(self):
        return "%r: Chapter %r" % (Book(self.booknum).name.title(), self.id)


db.create_all()
db.session.commit()
