from app.models import Chapter, Book
from tkinter import ttk, Tk, StringVar, N, S, W, E, Checkbutton, IntVar


def debug_log(text):
    debug = False

    if debug:
        debuglog = open("debuglog.txt", "a")
        debuglog.write(text + "\n")
        debuglog.close()


def blog_dog(*args):
    chapter = int(chapnum.get())
    book = str(bookname.get()).lower()
    booknum = Book[book].value
    root.destroy()

    f = open("blogposts\\%s%d.txt" % (book, chapter), "w")
    f.write("Title\nUPDATE: Chapter %d (%s)\n\n" % (chapter, book.title()))
    f.write("Tags\nupdate,iraedria,writing,fiction,iraedria update,%s\n" % book)
    f.write("(yeah this list is a work in progress i'll figure it out)\n\n\n")
    f.write("<p><b><a href='http://iraedria.ksadwin.com/%s/%d' target='_blank'>Read the latest chapter here.</a></b> Or, <i><a href='http://iraedria.ksadwin.com/' target='_blank'>start from the beginning.</a></i></p>\n\n" % (book, chapter))
    f.write("<p>Please reblog to spread the word!</p>\n\n")
    f.write("<p>See additional updates & content warnings for this chapter under the cut.</p>\n\n")
    f.write("[[MORE]]\n\n")

    # do a database lookup comparing update time for the new chapter to all other chapters
    newchapter = Chapter.query.filter_by(num=chapter, booknum=booknum).first()
    chaps = Chapter.query.filter_by(visible=True).all()
    debug_log(str(chaps))
    updatetime = newchapter.date_modified
    updatedchaps = []
    for c in chaps:
        debug_log("%.0f - %.0f = %.0f" % (updatetime, c.date_modified, updatetime - c.date_modified))
        if not (c.num >= newchapter.num and c.booknum == newchapter.booknum) and updatetime - c.date_modified < 15:
            updatedchaps.append(c)
    if len(updatedchaps) == 0:
        f.write("<p>No other chapters have updates.</p>\n\n")
    else:
        f.write("<p>These chapters have minor updates:</p>\n\n<ul>\n")
        for c in updatedchaps:
            if c.num == 0:
                f.write("  <li><a href='http://iraedria.ksadwin.com/%s/prologue' target='_blank'>Prologue (%s)</a></li>\n" % (Book(c.booknum).name, Book(c.booknum).name.title()))
            else:
                f.write("  <li><a href='http://iraedria.ksadwin.com/%s/%d' target='_blank'>Chapter %d (%s)</a></li>\n" % (Book(c.booknum).name, c.num, c.num, Book(c.booknum).name.title()))
        f.write("</ul>\n\n")

    f.write("<p>Content warnings for this chapter:</p>\n\n<ul>\n")
    for t in trigger_list:
        debug_log(str(trigger_dict[t].get()))
        if trigger_dict[t].get():
            f.write("  <li>%s</li>\n" % t)
    f.write("</ul>\n\n")
    f.write("<p>If you would like to add a content warning to the <a href='http://iraedria.tumblr.com/warnings'>global list</a>, or report a missing warning, <a href='http://iraedria.tumblr.com/ask'>send an ask.</a></p>\n\n")

    f.close()

if __name__ == "__main__":
    root = Tk()
    root.title("LETS MAKE A BLOG BOST")

    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    chapnum = StringVar()
    bookname = StringVar()

    chap_entry = ttk.Entry(mainframe, width=7, textvariable=chapnum)
    chap_entry.grid(column=2, row=1, sticky=(W, E))

    book_entry = ttk.Entry(mainframe, width=7, textvariable=bookname)
    book_entry.grid(column=2, row=2, sticky=(W, E))

    ttk.Label(mainframe, text="Chapter:").grid(column=1, row=1, sticky=E)
    ttk.Label(mainframe, text="Book:").grid(column=1, row=2, sticky=E)

    row = 2
    trigger_list = ["gore", "overt racism (non-fictional)"]
    trigger_dict = dict()
    for t in trigger_list:
        trigger_dict[t] = IntVar()
        l = Checkbutton(root, text=t, variable=trigger_dict[t])
        l.grid(column=1, row=row, sticky=W)
        row += 1

    ttk.Button(mainframe, text="Blog, dog", command=blog_dog).grid(column=2, row=row, sticky=W)
    mainframe.bind("<Return>", blog_dog)

    for child in mainframe.winfo_children():
        child.grid_configure(padx=5, pady=5)

    chap_entry.focus()
    root.mainloop()
