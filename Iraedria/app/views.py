from app import app, db
from flask import render_template, redirect, url_for, abort
from app.models import Chapter, Book


# VIEW FUNCTIONS

@app.errorhandler(404)
def page_not_found(e):
    """
    A flask built-in for displaying my personally handcrafted 404 page.
    :param e: the error, not that I ever use it, because I am a terrible person
    :return: a 404 page
    """
    return render_template('404.html'), 404


@app.route('/')
def index():
    """
    Just return the index page. No dynamic elements, I think.
    :return: static index template
    """
    return render_template("index.html")


@app.route('/<book>/prologue')
def prologue(book):
    """
    Finds the prologue file from the book directory and renders it with the special prologue template.
    :param book: title of book, case insensitive I guess.
    :return: the prologue if it exists, a 404 if it does not
    """
    try:
        bookenum = Book[book.lower()]
        c = Chapter.query.filter_by(num=0, booknum=bookenum.value).first()
        if c:
            return render_template("prologue.html", text=c.text, book=book)
        abort(404)
    except KeyError:
        abort(404)


@app.route('/<book>/<int:num>')
def chapter(book, num):
    """
    Finds a chapter in the directory given the book and chapter number, then heckin renders that template!
    :param book: title of book
    :param num: chapter number. if invalid, triggers a good ole 404
    :return: the diddly dang darn page!!
    """
    # this if statement is a small way in which i show my love for myself
    if num == 0:
        return redirect(url_for('prologue', book=book))
    try:
        bookenum = Book[book.lower()]
        c = Chapter.query.filter_by(num=num, booknum=bookenum.value).first()
        if c:
            return render_template("chapter.html", current=c, bookstr=book)
        abort(404)
    except KeyError:
        abort(404)


# FIXME: this does not work without AJAX tomfoolery, so there's an ugly redirect now
@app.route('/<book>/<int:num>/_like')
def _like(book, num):
    """
    Increments likes counter for a chapter.
    :param book: title of book
    :param num: chapter number
    :return: None.
    """
    try:
        bookenum = Book[book.lower()]
        c = Chapter.query.filter_by(num=num, booknum=bookenum.value).first()
        if c:
            c.likes += 1
        db.session.commit()
    except KeyError:
        pass
    return redirect(url_for('chapter', book=book, num=num))


@app.route('/bookmark')
def bookmark():
    """
    session variable will hold onto bookmarked page if I bother to implement this
    :return: for now, just the index
    """
    return redirect(url_for('index'))
