from app import app, db, login_manager, admin
from app.models import Name, Vote, User, Anon
from app.forms import SignUpForm, LoginForm, SuggestForm, SelectForm, ChangeDetailsForm, ChangePasswordForm
from flask import render_template, redirect, url_for, flash, jsonify, session
from flask_login import login_user, current_user, login_required, logout_user
import random
from passlib.apps import custom_app_context as pwd_context
from flask_admin.contrib.sqla import ModelView


login_manager.login_view = "signin"
login_manager.anonymous_user = Anon


# ADMIN VIEWS


class NameChangerModelView(ModelView):
    column_exclude_list = ['password', 'about', 'photo_url']
    column_display_pk = True

    def is_accessible(self):
        """
        Determines who can view the admin pages.
        :return: True if you're me, False if you're not.
        """
        return current_user.is_active and current_user.username == "sadmin"


admin.add_view(NameChangerModelView(User, db.session))
admin.add_view(NameChangerModelView(Name, db.session))
admin.add_view(NameChangerModelView(Vote, db.session))


# NON-VIEW FUNCTIONS


def delete_name_by_id(name_id, delete_votes=True):
    """
    Deletes a name and, along with it, its associated votes, if desired.
    :param name_id: primary key id for the Name to be deleted
    :param delete_votes: A flag to determine whether to delete associated Vote objects with Name being deleted
    :return: User listed as the suggester of the name
    """
    name = Name.query.get(name_id)
    if delete_votes:
        votes_to_delete = Vote.query.filter_by(nameID=name_id)
        for v in votes_to_delete:
            db.session.delete(v)
    suggester = name.suggester
    db.session.delete(name)
    db.session.commit()
    return suggester


def print_visited():
    """
    From my debugging days: concatonates a string containing all keys in session cookies (mostly usernames)
    :return: comma-separated string of usernames
    """
    namelist = ""
    for username in session.keys():
        namelist += username + ", "
    return namelist


def can_vote(u):
    """
    Determine whether or not current_user may vote on user u, based on whether current_user is anonymous or active, if
    u is private, or if current_user has voted on u previously.
    :param u: User potentially being voted on by current_user
    :return: True if current_user can vote on u, False otherwise. Always True for sadmin.
    """
    if not current_user.is_active:
        if u.username not in session.keys() and not u.private and u.active:
            app.logger.debug(u)
            return True
    elif current_user.username == "sadmin":
        if not u.active:
            flash("This user has been deactivated.")
        return True
    elif Vote.query.filter_by(voterID=current_user.id, userID=u.id).first() is None and u.active:
        app.logger.debug(u)
        return True
    return False


# TODO: make this more efficient than querying all users and pulling one at random, without so many repeats.
def generate_valid_user():
    """
    Queries User database for a User that current_user may cast a vote on, in conjunction with can_vote().
    :return: User object that meets conditions for voting, or None if no valid Users remain.
    """
    if current_user.is_active:
        users = list(User.query.filter_by(active=True))
    else:
        users = list(User.query.filter_by(active=True, private=False))
    while users:
        u = random.choice(users)
        if can_vote(u):
            return u
        users.remove(u)
    # all users have been visited, return error condition
    return None


def validate_suggest_form(f, u):
    """
    Generates a Name and Vote object based on data from a validated SuggestForm.
    :param f: SuggestForm (validated and submitted)
    :param u: User to whom this suggestion was submitted
    """
    if current_user.is_active:
        suggester = current_user
    else:
        suggester = None
        session[u.username] = True
    n = Name(f.name.data, u, suggester)
    v = Vote(n, u, suggester)

    db.session.add(n)
    db.session.add(v)
    db.session.commit()


def validate_select_form(f, u):
    """
    Generates a Vote object based on data from a validated SelectForm.
    :param f: SelectForm (validated and submitted)
    :param u: User to whom this selection was submitted
    """
    n = Name.query.get(f.name.data)
    n.score += 1
    if current_user.is_active:
        suggester = current_user
    else:
        suggester = None
        session[u.username] = True
    v = Vote(n, u, suggester)
    db.session.add(v)
    db.session.commit()


# THE VIEWS

@app.route('/signin/', methods=('GET', 'POST'))
def signin():
    """
    The page on which a user sign in or sign up, depending on whether the SignUpForm or the LoginForm is submitted.
    :return: signin.html rendered with both forms
    """
    if current_user.is_active:
        flash("You are already signed in.")
        return redirect(url_for("index"))
    signup = SignUpForm()
    login = LoginForm()
    if login.validate_on_submit():
        username = login.username_l.data.lower()
        password = login.password_l.data
        u = User.query.filter_by(username=username).first()
        if u:
            if not u.is_active:
                flash("This account has been deactivated because of too many complaints from users.")
            elif pwd_context.verify(password, u.password):
                login_user(u)
                flash("You're in.")
                return redirect(url_for("public_profile", name=u.username))
            else:
                flash("Wrong password.")
        else:
            flash('Never heard of you.')
    if signup.validate_on_submit():
        username = signup.username_s.data.lower()
        password = pwd_context.encrypt(signup.password_s.data)
        blurb = signup.about_s.data
        url = signup.url_s.data
        badu = User.query.filter_by(username=username).first()
        if not badu:
            u = User(username, password, url, blurb)
            db.session.add(u)
            db.session.commit()
            login_user(u)
            flash("Welcome.")
            return redirect(url_for("index"))
        else:
            flash("Sorry, that one's taken.")
    return render_template("signin.html", signup=signup, login=login)


# FIXME: this gets called more than the standard, let's say, once per click. and it hecks up the names.
@app.route('/', methods=('GET', 'POST'))
def index():
    """
    Redirects to a randomly generated user's profile for voting.
    :return: redirect to public_profile() with generated user, or if no valid user is found, error.html
    """
    u = generate_valid_user()
    if u is None:
        return render_template("error.html", message="Either you have voted for every user on the website or a table "
                                                     "got dropped. If it's the former, thanks! If it's the latter, "
                                                     "please do not hold it against me. I am but a simple college "
                                                     "student.")
    return redirect(url_for('public_profile', name=u.username))


@app.route('/about/')
def about():
    """
    A simple page to explain the purpose and operation of NameChanger.
    :return: about.html
    """
    return render_template("about.html")


@app.route('/user/<name>/', methods=('GET', 'POST'))
def public_profile(name):
    """
    The public page for a user. Can only be viewed by someone who does not have a current vote on this user, and, if
    the user is private, is logged in. Either the SuggestForm or SelectForm will appear pending on user.suggestions.
    :param name: username of User to display
    :return: index.html rendered with user details and appropriate form
    """
    name = name.lower()
    user = User.query.filter_by(username=name).first()
    if user is None:
        flash("User not found.")
        return redirect(url_for("index"))
    elif user != current_user:
        if not can_vote(user):
            flash("You cannot vote on this user's profile. It may be private, deactivated, or you may have already "
                  "voted.")
            return redirect(url_for("index"))
    if user.suggestions:
        f = SuggestForm()
        if f.validate_on_submit():
            validate_suggest_form(f, user)
            return redirect(url_for('index'))
    else:
        names = Name.query.filter_by(userID=user.id).order_by('score').all()
        f = SelectForm()
        f.name.choices = [(n.id, n.name) for n in names]
        if f.validate_on_submit():
            validate_select_form(f, user)
            return redirect(url_for('index'))

    return render_template("index.html", form=f, user=user)


@app.route('/profile/', methods=('GET', 'POST'))
@login_required
def private_profile():
    """
    The settings page for current_user. Here current_user may toggle suggestions, private, delete or report names,
    change about & photo with a shoddy ChangeDetailsForm, change password with an acceptable ChangePasswordForm, or
    permanently delete the account.
    :return: profile.html rendered with list of suggested names for current_user amd forms
    """
    names = Name.query.filter_by(userID=current_user.get_id()).all()

    # TODO: implement a new form to change account details you lazy trashbag
    form_d = ChangeDetailsForm(csrf_enabled=False)
    form_p = ChangePasswordForm()
    if form_p.validate_on_submit():
        if pwd_context.verify(form_p.current_password.data, current_user.password):
            user = User.query.get(current_user.id)
            user.password = pwd_context.encrypt(form_p.new_password.data)
            db.session.commit()
            flash("Changes saved.")
            return redirect(url_for("private_profile"))
        else:
            flash("Incorrect password.")
            return redirect(url_for("private_profile"))
    if form_d.validate_on_submit():
        user = User.query.get(current_user.id)
        if form_d.about.data != "":
            user.about = form_d.about.data
        app.logger.debug("result: "+user.about)
        if form_d.url.data != "":
            user.photo_url = form_d.url.data
        db.session.commit()
        flash("Changes saved.")
        return redirect(url_for("private_profile"))

    return render_template("profile.html", names=names, form_d=form_d, form_p=form_p)


@app.route('/cookies/')
def view_cookies():
    """
    A basic page to display current cookies. Uses print_visited()
    :return: error.html rendered to display comma-separated cookies
    """
    return render_template("error.html", message=print_visited())


# TODO: do not leave this in the deployed app I swear to every god
@app.route('/delete_cookies/')
def delete_cookies():
    """
    I LEFT THIS IN THE DEPLOYED APP I'M A PIECE OF TRASH OH MY GOD
    :return: well now I'm going to return a joke page that contains a screenshot of this function
    """
    # session.clear()
    return url_for("static", filename="img/imtrash.png")


@login_manager.user_loader
def load_user(user_id):
    """
    Component of flask-login to load a successfully authenticated user.
    :param user_id: primary key of User to load
    :return: User object from db
    """
    return User.query.get(user_id)


@app.route("/logout/")
@login_required
def logout():
    """
    The link that makes you log out.
    :return: redirect to index with flashed logout message
    """
    logout_user()
    flash("You've successfully logged out.")
    return redirect(url_for("index"))


@app.route("/delete_account/")
@login_required
def delete_account():
    """
    Deletes current_user from database, including nullifying their foreign key relations on Names and Votes as
    suggesters and voters respectively, and deleting Names and Votes in which they are the recipient user.
    Also logs them out, because I'm a little afraid of what would happen if I didn't do that.
    :return: redirect to index with flashed goodbye message
    """
    user = User.query.get(current_user.id)
    for name in Name.query.filter_by(suggesterID=user.id):
        name.suggester = None
    for name in Name.query.filter_by(userID=user.id):
        db.session.delete(name)
    for vote in Vote.query.filter_by(voterID=user.id):
        vote.voter = None
    for vote in Vote.query.filter_by(userID=user.id):
        db.session.delete(vote)
    logout_user()
    db.session.delete(user)
    flash("Sorry to see you go.")
    return redirect(url_for("index"))


# invisible AJAX places

@app.route("/_toggle_suggestions/")
@login_required
def toggle_suggestions():
    """
    Changes current_user.suggestions from one to the other, whichever it was. Clears all vottes in which current_user
    is the recipient because it's a whole new ballgame now.
    :return: JSON object of new value of current_user.suggestions
    """
    # current_user is a copy, find the original
    user = User.query.get(current_user.id)
    if user.suggestions:
        user.suggestions = False
    else:
        user.suggestions = True
    votes_to_delete = Vote.query.filter_by(userID=user.id).all()
    for v in votes_to_delete:
        db.session.delete(v)
    db.session.commit()
    return jsonify(s=user.suggestions)


@app.route("/_toggle_privacy/")
@login_required
def toggle_privacy():
    """
    Changes current_user.private from one to the other, whichever it was. If user.private no anonymous users may view
    user's profile.
    :return: JSON object of new value of current_user.private
    """
    # current_user is a copy, find the original
    user = User.query.get(current_user.id)
    if user.private:
        user.private = False
    else:
        user.private = True
    db.session.commit()
    return jsonify(s=user.private)


@app.route("/_delete-<int:name_id>/")
@login_required
def delete_name(name_id):
    """
    Removes selected name from db.
    :param name_id: primary key of Name to delete
    :return: JSON object containing deleted name id
    """
    delete_name_by_id(name_id)
    return jsonify(id=name_id)


@app.route("/_report-<int:name_id>/")
@login_required
def report_name(name_id):
    """
    Removes selected name from db and increments suggester's flags, then checks to see if user should be deactivated
    on account of too many flags. current_user will be informed if the suggester has been deactivated was the idea?
    :param name_id: primary key of Name to delete and report
    :return: JSON object containing reported name id and suggester's active status
    """
    reported = delete_name_by_id(name_id, delete_votes=False)
    # flag to notify whether anon or user suggested the offensive name
    is_active = False
    if reported:
        reported.flags += 1
        if reported.flags >= 3:
            reported.active = False
        is_active = True
    db.session.commit()
    return jsonify(id=name_id, active=is_active)
