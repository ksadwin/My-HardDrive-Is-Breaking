from app import db
import datetime


class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    summary = db.Column(db.String(1024))
    filename = db.Column(db.String(64))

    def __init__(self, name, summary, filename):
        self.name = name
        self.summary = summary
        self.filename = filename

    def __repr__(self):
        return "Book %r: %r" % self.id, self.name


class Chapter(db.Model):
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True)
    summary = db.Column(db.String(128))
    date_added = db.Column(db.Date)
    date_modified = db.Column(db.Date)

    bookId = db.Column(db.Integer, db.ForeignKey('book.id'))
    book = db.relationship('Book', foreign_keys=bookId)

    def __init__(self, summary, book):
        self.summary = summary
        self.date_added = datetime.date
        self.date_modified = self.date_added
        self.book = book

    def __repr__(self):
        return "Chapter %r" % self.id


db.create_all()
db.session.commit()
