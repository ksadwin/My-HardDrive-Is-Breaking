from app import db
from bs4 import BeautifulSoup
from config import basedir
import os
from app.models import Chapter, get_text_from_path, Book


PATH_TO_BASE_TEMPLATE = os.path.join(basedir, 'templates/base.html')
PATH_TO_NOVEL = os.path.join(basedir, 'static/text')


def create_book_dropdown(soup, b):
    # find the ul that contains navbar links, given id chapter-list
    cl = soup.find(id="chapter-list")

    # create new navbar item with class dropdown for new book
    dropdown_li = soup.new_tag("li")
    dropdown_li['class'] = "dropdown"

    # create link that activates dropdown
    link = soup.new_tag("a", href="#")
    link['class'] = "dropdown-toggle"
    link['data-toggle'] = "dropdown"
    link['role'] = "button"
    link['aria-haspopup'] = "true"
    link['aria-expanded'] = "false"

    # create a caret! how nice
    caret = soup.new_tag("span")
    caret['class'] = "caret"

    # create ul to be placed inside book dropdown. if i weren't too lazy to retest this would be the return value
    b_ul = soup.new_tag("ul")
    b_ul['class'] = "dropdown-menu"
    b_ul['id'] = b.lower()

    # label the dropdown with as "<Book> v" where v is a lil caret how nice
    link.append(b+" ")
    link.append(caret)

    # put the link and the dropdown list into the encapsulating navbar item
    dropdown_li.append(link)
    dropdown_li.append(b_ul)

    # and put that navbar item into the navbar list
    cl.append(dropdown_li)


def update():
    # hold onto the orig_text in case of writing error later, can write this back to file
    orig_text = get_text_from_path(PATH_TO_BASE_TEMPLATE)
    soup = BeautifulSoup(orig_text, "html.parser")
    books = os.listdir(PATH_TO_NOVEL)  # gets immediate children of PATH (i.e. book folders)
    # NOTE: NOTHING ELSE CAN BE IN THIS FOLDER

    for b in books:  # b is capitalized as in path!
        # find where in the html the chapters for this book are listed, or make it if it's a new book
        b_ul = soup.find(id=b.lower())
        if b_ul is None:
            create_book_dropdown(soup, b)
            b_ul = soup.find(id=b.lower())

        book_path = os.path.join(PATH_TO_NOVEL, b)
        chapters = os.listdir(book_path)  # gets immediate children of path (i.e. chapter files)
        # NOTE: NOTHING ELSE CAN BE IN THIS FOLDER

        for c in chapters:  # of form 'x.html'
            chapter_path = os.path.join(book_path, c)
            c = os.path.splitext(c)[0]  # now in form 'x' if i know anything at all
            current_chapter = Chapter.query.filter_by(booknum=Book[b.lower()].value, num=int(c)).first()
            mtime = os.path.getmtime(chapter_path)

            if current_chapter is None:
                # here's the line where you actually add something to the database! I know you were looking for it.
                db.session.add(Chapter(chapter_path, b))
            elif mtime > current_chapter.date_modified:
                current_chapter.date_modified = mtime
                current_chapter.text = get_text_from_path(chapter_path)

            # note to future self: keep this in this outer scope, not in the if statement about the chapter existing
            # there may come a day when you may need to add the links even though the files are not new
            # don't you remember how often you screw up...?
            c_id = "%s-%s" % (b.lower(), c)
            if soup.find(id=c_id) is None:
                # I started to make a separate function for adding a chapter link but it needed like 5 parameters so
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
    except Exception:  # yeah I KNOW it's vague python I just really don't want to accidentally delete this whole page
        f.write(orig_text)
        f.close()

    db.session.commit()


def main():
    update()

if __name__ == "__main__":
    main()
