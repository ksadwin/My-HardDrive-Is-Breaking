import os
import unittest
from app import app, db
from config import basedir
from app.models import User, Vote, Name


# TODO: how to submit a wtform with app.post()? Current ideas are to download wireshark and capture my own packets

class NameChangerTestCase(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'testdb.sqlite')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = "butts heheheh"
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_user(self, context):
        u = User("testuser"+context, "testpassword", "testabout", "testphoto")
        db.session.add(u)
        db.session.commit()

    def create_name(self, user, suggester, namestr):
        n = Name(namestr, user, suggester)
        db.session.add(n)
        db.session.commit()

    def create_vote(self, user, voter, name):
        v = Vote(name, user, voter)
        db.session.add(v)
        db.session.commit()

    def login(self, username, password):
        return self.app.post('/signin/', data=dict(
            username_1=username,
            password_l=password,
            submit_l=""
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout/', follow_redirects=True)

    def test_about(self):
        request = self.app.get('/about/')
        page = request.data.decode('utf-8')
        self.assertIn('What the heck is NameChanger?', page)

    def test_profile(self):
        self.create_user("profile")

        # existing user
        request = self.app.get("/user/testuserprofile", follow_redirects=True)
        page = request.data.decode('utf-8')
        self.assertIn('testabout', page)

        # bad username
        request = self.app.get("/user/wepfhwsioh", follow_redirects=True)
        page = request.data.decode('utf-8')
        self.assertIn("User not found", page)

        # private user, attempting to view without logging in (should fail)
        u = User.query.filter_by(username='testuserprofile').first()
        u.private = True
        db.session.commit()
        request = self.app.get("/user/testuserprofile", follow_redirects=True)
        page = request.data.decode('utf-8')
        self.assertIn("You cannot vote on this user", page)

        # inactive user
        u.private = False  # reverse the privacy from before to prove it's the inactivity at play here
        u.active = False
        db.session.commit()
        request = self.app.get("/user/testuserprofile", follow_redirects=True)
        page = request.data.decode('utf-8')
        self.assertIn("You cannot vote on this user", page)

        # TODO: test privacy with logged-in user once you figure out how to log in

    # def test_delete_user(self):
    #     self.create_user("delete_user1")
    #     self.create_user("delete_user2")
    #     u1 = User.query.filter_by(username="testuserdelete_user1").first()
    #     u2 = User.query.filter_by(username="testuserdelete_user2").first()
    #     self.create_name(u1, u2, "bob")
    #     self.create_name(u2, u1, "gary")
    #     nfor1 = Name.query.filter_by(name="bob").first()
    #     nfrom1 = Name.query.filter_by(name="gary").first()
    #     self.create_vote(u1, u2, nfor1)
    #     self.create_vote(u2, u1, nfrom1)
    #     # TODO: just kidding i need to be logged in to actually test the delete page
    #     # FIXME: once I figure out logins, get rid of the unsightly way of creating these votes. use forms.

    # def test_login(self):
    #
    #     request = self.login('testuser1', 'testpassword1')
    #     page = request.data.decode('utf-8')
    #     print(page)
    #     self.assertIn("You're in.", page)
    #     request = self.logout()
    #     assert "You've successfully logged out" in request.data


if __name__ == '__main__':
    unittest.main()
