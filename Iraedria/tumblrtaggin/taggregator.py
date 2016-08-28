from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import logging

MAX_POSTS = 500
AGE_OF_OBSOLESCENCE = timedelta(weeks=3)
# this may all be useless because tumblr only preloads 50 pages rip in pepperoni


def get_archive(username):
    """
    Constructs URL in the format http://username.tumblr.com/archive and fetches it with requests
    :param username: tumblr username as a string
    :return: BeautifulSoup object of requested page
    :raises: requests.HTTPError (if blog does not exist)
    """
    archive_url = "http://"+username+".tumblr.com/archive"
    r = requests.get(archive_url)
    if r.status_code != 200:
        raise requests.HTTPError
    return BeautifulSoup(r.text, "html.parser")


def is_current(match):
    """
    Given the soup match containing all the good stuff, pull out the date string, convert it to a date object,
    and check it against the predetermined expiration date for fads: AGE_OF_OBSOLESCENCE
    :param match: BeautifulSoup match
    :return: True if recent, False if obsolete.
    """
    str_date = match.find(class_="post_date").get_text()  # of form Aug 8, 2016
    logging.debug("Date: "+str_date)
    post_date = datetime.strptime(str_date, "%b %d, %Y")
    age = datetime.today() - post_date
    if age > AGE_OF_OBSOLESCENCE:
        return False
    else:
        return True


def add_tags_to_dict(match, tag_dict):
    """
    Adds tags of a (previously validated) post to a growing dictionary of tags.
    :param match: BeautifulSoup match
    :param tag_dict: current dictionary of tags
    :return: new and improved tag_dict
    """
    logging.debug("add_tags_to_dict > match = "+str(match))
    tag_match = match.find(class_="tags")
    # check if match is found because the div does not exist if the post is not tagged
    if tag_match is None:
        return
    str_tags = tag_match.get_text()  # lots of whitespace possible. thanks staff
    tags = str_tags.split("#")
    tags.pop(0)  # the first tag is an empty
    logging.debug(tags)
    for t in tags:
        t = t.strip()
        t = t.lower()
        if t in tag_dict.keys():
            tag_dict[t] += 1
        else:
            tag_dict[t] = 1


def make_tag_dict(soup):
    """
    Create dictionary of tags to frequency based on at most MAX_POST posts in the past AGE_OF_OBSOLESCENCE timespan.
    :param soup: BeautifulSoup object of archive page
    :return: dictionary of tags, e.g. {"#pokemon" : 3, "#ztd" : 10}
    :raises: IndexError (if empty blog is found)
    """
    matches = soup.find_all(class_="post_glass")  # TODO: does every post have this class...? let's hope
    logging.debug(matches)

    # three conditions must be met to continue the loop:
    # 1. there are posts remaining to analyze (having an empty blog will trigger IndexError)
    # 2. the post being analyzed has not exceeded AGE_OF_OBSOLESCENCE
    # 3. the number of currently analyzed posts does not exceed MAX_POSTS
    counter = 0
    m = matches.pop(0)  # IndexError possible
    tag_dict = dict()
    while is_current(m) and counter <= MAX_POSTS:
        counter += 1
        add_tags_to_dict(m, tag_dict)
        try:
            m = matches.pop(0)
        except IndexError:  # no posts remain to analyze
            logging.info("No more posts after "+str(counter))
            return tag_dict
    logging.debug(tag_dict)
    logging.debug(counter)
    return tag_dict


def find_tags(username):
    """
    the whole shebang
    :param username: string tumblr username
    :return: list (max ten) of most popular tags in order from high to low
    """
    try:
        archive_soup = get_archive(username)
        tag_dict = make_tag_dict(archive_soup)
        tag_list = list()
        for tag in sorted(tag_dict, key=tag_dict.get, reverse=True):
            logging.info(tag+":"+str(tag_dict[tag]))
            if tag_dict[tag] > 1:
                tag_list.append(tag)
            if len(tag_list) > 10:
                return tag_list
        return tag_list
    except requests.HTTPError:
        logging.error("Blog does not exist.")
    except IndexError:
        logging.error("No posts found.")


def find_tags_test():
    """
    Uses a predownloaded html page of airdeari's tumblr (from 8/8/2016) while airdeari tests his code
    :return: none (prints tags to console)
    """
    logging.info("Performing test run using static html file")
    f = open("archive.html", "r")
    archive = f.read()
    f.close()
    logging.debug(archive)
    soup = BeautifulSoup(archive, "html.parser")
    try:
        tag_dict = make_tag_dict(soup)
        for tag in sorted(tag_dict, key=tag_dict.get, reverse=True):
            print(tag, ":", tag_dict[tag])
    except IndexError:
        logging.error("No posts found.")


def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    username = input("Enter tumblr username: ")
    print(find_tags(username))
    # print(find_tags_test())


if __name__ == "__main__":
    main()

