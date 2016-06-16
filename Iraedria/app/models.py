from app import db
import time
from config import PATH_TO_NOVEL, PATH_TO_BASE_TEMPLATE, Book
import os
from bs4 import BeautifulSoup
from html import unescape


def get_text_from_path(fpath):
    f = open(fpath, "r")
    text = f.read()
    f.close()
    return text


class Chapter(db.Model):
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True)
    num = db.Column(db.Integer)
    text = db.Column(db.String)  # gave it no length parameter, let's see what happens?
    date_added = db.Column(db.Integer)
    date_modified = db.Column(db.Integer)
    booknum = db.Column(db.Integer)

    def __init__(self, filename, bookstr):
        bookstr = bookstr.lower()
        self.booknum = Book[bookstr].value
        self.num = os.path.splitext(os.path.basename(filename))[0]

        self.date_added = time.time()
        self.date_modified = os.path.getmtime(filename)

        self.text = get_text_from_path(filename)

    def __repr__(self):
        return "%r: Chapter %r" % (Book(self.booknum).name.title(), self.id)


def update():
    orig_text = get_text_from_path(PATH_TO_BASE_TEMPLATE)
    soup = BeautifulSoup(orig_text, "html.parser")
    books = os.listdir(PATH_TO_NOVEL)
    for b in books:  # b is capitalized as in path!
        b_ul = soup.find(id=b.lower())
        if b_ul is None:
            cl = soup.find(id="chapter-list")
            dropdown_li = soup.new_tag("li")
            dropdown_li['class'] = "dropdown"
            link = soup.new_tag("a", href="#")
            link['class'] = "dropdown-toggle"
            link['data-toggle'] = "dropdown"
            link['role'] = "button"
            link['aria-haspopup'] = "true"
            link['aria-expanded'] = "false"
            caret = soup.new_tag("span")
            caret['class'] = "caret"
            b_ul = soup.new_tag("ul")
            b_ul['class'] = "dropdown-menu"
            b_ul['id'] = b.lower()
            link.append(b+" ")
            link.append(caret)
            dropdown_li.append(link)
            dropdown_li.append(b_ul)
            cl.append(dropdown_li)
            b_ul = soup.find(id=b.lower())
        book_path = os.path.join(PATH_TO_NOVEL, b)
        chapters = os.listdir(book_path)
        for c in chapters:  # of form 'x.html'
            chapter_path = os.path.join(book_path, c)
            c = os.path.splitext(c)[0]  # now comes in form 'x' if i know anything at all
            current_chapter = Chapter.query.filter_by(booknum=Book[b.lower()].value, num=int(c)).first()
            mtime = os.path.getmtime(chapter_path)
            if current_chapter is None:
                db.session.add(Chapter(chapter_path, b))
            elif mtime > current_chapter.date_modified:
                current_chapter.date_modified = mtime
                current_chapter.text = get_text_from_path(chapter_path)
            c_id = "%s-%s" % (b.lower(), c)
            if soup.find(id=c_id) is None:
                li = soup.new_tag("li")
                li['id'] = c_id
                link = soup.new_tag("a")
                link['href'] = "{{ url_for('chapter', num=%s, book='%s') }}" % (c, b.lower())
                if c == "0":
                    link.append("Prologue")
                else:
                    link.append("Chapter "+c)
                li.append(link)
                b_ul.append(li)

    f = open(PATH_TO_BASE_TEMPLATE, "w")
    try:
        f.write(str(soup))
        f.close()
    except Exception:  # yeah I KNOW it's vague python, I just rly don't want to accidentally delete this whole page
        f.write(orig_text)
        f.close()

    db.session.commit()


db.create_all()
db.session.commit()
