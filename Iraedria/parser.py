from bs4 import BeautifulSoup
import sys

TEST_FILE_PATH = r"C:\Users\Asus\Documents\github\My-HardDrive-Is-Breaking\Iraedria\static\text\Vega\3.html"


def get_text_from_path(fpath):
    f = open(fpath, "r")
    text = f.read()
    f.close()
    return text


def write_to_file(text, fpath):
    f = open(fpath, "w")
    f.write(text)
    f.close()


def add_attrs_to_p(p):
    """
    If I later want to add any tags to each paragraph, I can do it here.
    :param p: BeautifulSoup tag <p>
    :return: BeautifulSoup tag <p> with desired attrs
    """
    return p


def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    paras = soup.find_all("p", "MsoNormal")
    final = ""
    first = True
    for i in range(len(paras)):
        p = paras[i]
        del p['class']
        del p['style']
        # p = add_attrs_to_p(p)
        bad_tags = ["span", "a"]
        for tag in bad_tags:
            for match in p.find_all(tag):
                if match.get('class') == ["MsoCommentReference"]:  # if "MsoCommentReference" in match.get('class')?
                    match.extract()
                else:
                    match.unwrap()
        # special dream markers
        if p.string == "START_DREAM":
            if final != "":
                final += "</div>\n"
            final += "<div class='container dream'>\n"
            first = True
        elif p.string == "END_DREAM":
            final += "</div>\n"
            if i != len(paras) - 1:
                final += "<div class='container page'>\n"
                first = True
        else:
            if final == "":
                final += "<div class='container page'>\n"
            if first:
                # dropcap time!!!
                first = False
                text = str(p)
                final += "%s<span class=\"drop-cap\">%s</span>%s" % (text[0:3], text[3], text[4:])
            else:
                final += str(p)+"\n"
    # do not add the last </div> to final. it is included in chapter.html
    return final


def test():
    body = parse(get_text_from_path(TEST_FILE_PATH))
    write_to_file(body, TEST_FILE_PATH)
    # body should actually be inserted into a template but hey this is a test


def use_argument():
    fpath = sys.argv[1]
    body = parse(get_text_from_path(fpath))
    write_to_file(body, fpath)


def main():
    use_argument()
    # test()

if __name__ == "__main__":
    main()
