from app import app, db, login_manager, admin
from app.models import Name, Vote, User, Anon
from app.forms import SignUpForm, LoginForm, SuggestForm, SelectForm
from flask import render_template, redirect, url_for, flash, jsonify, session
from flask_login import login_user, current_user, login_required, logout_user
import random
from passlib.apps import custom_app_context as pwd_context
from flask_admin.contrib.sqla import ModelView


login_manager.login_view = "signin"
login_manager.anonymous_user = Anon


# ADMIN VIEWS


class NameChangerModelView(ModelView):

    def is_accessible(self):
        return current_user.is_active and current_user.username == "sadmin"


admin.add_view(NameChangerModelView(User, db.session))
admin.add_view(NameChangerModelView(Name, db.session))
admin.add_view(NameChangerModelView(Vote, db.session))


# NON-VIEW FUNCTIONS


def delete_name_by_id(name_id, delete_votes=True):
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
    namelist = ""
    for username in session.keys():
        namelist += username + ", "
    return namelist


def can_vote(u):
    if not current_user.is_active:
        if u.username not in session.keys() and not u.private:
            app.logger.debug(u)
            return True
    elif Vote.query.filter_by(voterID=current_user.id, userID=u.id).first() is None:
        app.logger.debug(u)
        return True
    return False


def generate_valid_user():
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
            # FIXME: this message pops up when you sign up correctly
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
    u = generate_valid_user()
    if u is None:
        return render_template("error.html", message="Either you have voted for every user on the website or a table "
                                                     "got dropped. If it's the former, thanks! If it's the latter, "
                                                     "please do not hold it against me. I am but a simple college "
                                                     "student.")
    return redirect(url_for('public_profile', name=u.username))


@app.route('/about/')
def about():
    return render_template("about.html")


@app.route('/user/<name>/', methods=('GET', 'POST'))
def public_profile(name):
    name = name.lower()
    user = User.query.filter_by(username=name).first()
    if user is None:
        flash("User not found.")
        return redirect(url_for("index"))
    elif user != current_user:
        if not can_vote(user):
            flash("You cannot vote on this user's profile. It may be private, or you may have already voted.")
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
    names = Name.query.filter_by(userID=current_user.get_id()).all()

    # TODO: implement a new form to change account details you lazy trashbag
    """
    s = SignUpForm()
    # current_user is a copy, find the original
    user = User.query.get(current_user.id)
    s.username.data = user.username
    s.about.data = user.about
    s.url.data = user.photo_url
    if s.validate_on_submit():
        if pwd_context.verify(s.password.data, user.password):
            user.username = s.username.data
            user.photo_url = s.url.data
            user.about = s.about.data
            db.session.commit()
            flash("Changes saved.")
            return redirect(url_for("private_profile"))
        else:
            flash("Incorrect password.")
            return redirect(url_for("private_profile"))
    """
    return render_template("profile.html", names=names)


@app.route('/cookies/')
def view_cookies():
    return render_template("error.html", message=print_visited())


# TODO: do not leave this in the deployed app I swear to every god
@app.route('/delete_cookies/')
def delete_cookies():
    session.clear()
    return render_template("error.html", message=print_visited())


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    flash("You've successfully logged out.")
    return redirect(url_for("index"))


@app.route("/delete_account/")
@login_required
def delete_account():
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
    delete_name_by_id(name_id)
    return jsonify(id=name_id)


@app.route("/_report-<int:name_id>/")
@login_required
def report_name(name_id):
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
