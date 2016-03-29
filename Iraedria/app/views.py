from app import app
from flask import render_template, redirect, url_for


# intro page, general description, in ~/static/index.html
@app.route('/')
def index():
    return render_template("../static/index.html")


# book intro page with chapter list. dynamically generates title, summary, bg img, chapters & descriptions
@app.route('/<book>')
def book_index(book):
    # a placeholder page, just the prologue
    return render_template("../static/prologue.html")


# chapter page. use 0 for prologue I guess
@app.route('/<book>/<num>')
def chapter(book, num):
    # a placeholder page, just the first chapter
    return render_template("../static/chapter1.html")


# session variable will hold onto bookmarked page if I bother to implement this
@app.route('/bookmark')
def bookmark():
    # a placeholder page, just the first chapter
    return render_template("../static/chapter1.html")
