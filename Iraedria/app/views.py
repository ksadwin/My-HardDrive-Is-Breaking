from app import app, db
from flask import render_template, redirect, url_for, abort, jsonify
from app.models import Chapter, Book
from app.forms import TagForm
from urllib.parse import quote_plus

from tumblrtaggin.taggregator import find_tags


# VIEW FUNCTIONS

@app.errorhandler(404)
def page_not_found(e):
    """
    A flask built-in for displaying my personally handcrafted 404 page.
    :param e: the error, not that I ever use it, because I am a terrible person
    :return: a 404 page
    """
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """
    A flask built-in for displaying my personally handcrafted 500 page that just reminds me where to find the logs.
    :param e:
    :return: a very simple message
    """
    return """<h1>Internal Server Error</h1>
    <p>The server encountered an internal error and was unable to complete your request.  Either the server is
    overloaded or there is an error in the application.</p>
    <p><i>note from admin to self: /var/log/apache2/error.log</i></p>"""


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


# SECRET VIEWS

@app.route('/stats')
def view_likes():
    """
    displays likes for each chapter so I don't have to dig through the server to pull the database every time
    :return: extremely bland page displaying likes as a list
    """
    chaps = Chapter.query.all()
    out = ""
    for c in chaps:
        out += "<p>Chapter %d: %d</p>\n" % (c.num, c.likes)
    return out


@app.route('/bookmark')
def bookmark():
    """
    session variable will hold onto bookmarked page if I bother to implement this
    :return: for now, just the index
    """
    return redirect(url_for('index'))


# TODO: make color correspond to text color, not background color
@app.route('/taggregator/tumblr/<username>/<int:height>/<int:width>/<color>/')
def taggregator(username, height, width, color):
    """
    This is the cutest thing I've ever made, and I'm proud.
    :param username: tumblr username
    :param height: height of div
    :param width: width of div
    :param color: link color
    :return: an html page with your top 10 (or fewer) tumblr tags
    """
    # TODO: Not this anymore
    top_tags = find_tags(username)
    return render_template("taggregator.html", username=username, top_tags=top_tags, height=height, width=width,
                           color=color)


@app.route('/taggregator/tumblr/', methods=('GET', 'POST'))
def taggremaker():
    """
    Page to generate taggregator iframe. Starts with example iframe for tumblr user airdeari.
    Uses TagForm to make a new taggregation for the tumblr user and styling of choice.
    :return: the page I just described
    """
    u = "airdeari"
    c = "fffafb"
    h = 200
    w = 200
    iframe_code = iframe_code = '<iframe src="http://iraedria.ksadwin.com' +\
                  url_for('taggregator', username=u, color=c, height=h, width=w) +\
                  '" frameBorder="0" scrolling="no"></iframe>'
    f = TagForm(csrf_enabled=False)  # FIXME: or dont. fite me
    if f.validate_on_submit():
        u = f.username.data
        c = f.color.data
        h = f.height.data
        w = f.width.data
        iframe_code = '<iframe src="http://iraedria.ksadwin.com' +\
                      url_for('taggregator', username=u, color=c, height=h,width=w) +\
                      '" frameBorder="0" scrolling="no"></iframe>'
        return render_template("tagremaker.html", form=f, u=u, c=c, w=w, h=h, iframe_code=iframe_code)
        # I should have just made this form myself with JS probably
    return render_template("tagremaker.html", form=f, u=u, c=c, w=w, h=h, iframe_code=iframe_code)


# did you know ctrl+? comments things in pycharm?? what a handy misplacement of fingers I just had
@app.route("/test")
def test():
    url = url_for('taggregator', username="airdeari", height=500, width=500, color="ff0000")
    html = "<p>with any luck here's an iframe</p><iframe src='"\
           + url + "' height=500 width=500 scrolling='no' frameBorder=0></iframe>"
    return html


# INVISIBLE AJAX PLACES

@app.route("/_taggregator/tumblr/<username>")
def retrieve_tags(username):
    """
    BY THE POWER OF AJAX I SHALL PERFORM ACTIONS IN THE BACKGROUND!
    :param username: tumblr user to scrape
    :return: json array of top tags in order
    """
    top_tags = find_tags(username)
    tag_string = ""
    for i in range(len(top_tags)):
        words_in_tag = top_tags[i].split()
        url_safe_tag = ""
        for w in words_in_tag:
            url_safe_tag += quote_plus(w) + "-"
        # remove trailing hyphen
        url_safe_tag = url_safe_tag[:-1]

        tag_string += "<a href='http://"+username+".tumblr.com/tagged/"+url_safe_tag+"' target='_blank'>#"+top_tags[i]\
                      + "</a> "

    return jsonify(tag_list=tag_string)
