from app import app, db, login_manager
from app.models import Name, Vote, User, Anon
from app.forms import SignUpForm, LoginForm, SuggestForm, SelectForm
from flask import render_template, redirect, url_for, flash, jsonify, session
from flask_login import login_user, current_user, login_required, logout_user
import random
from passlib.apps import custom_app_context as pwd_context


login_manager.login_view = "signin"
login_manager.anonymous_user = Anon


# NON-VIEW FUNCTIONS

def public_logged_in(u):
    if u.suggestions:
        f = SuggestForm()
        if f.validate_on_submit():
            if current_user.is_active:
                suggester = current_user
            else:
                suggester = None
                session['visited'].append(u.username)
            n = Name(f.name.data, u, suggester)
            v = Vote(n, u, suggester)

            db.session.add(n)
            db.session.add(v)
            db.session.commit()
            return redirect(url_for("index"))
    else:
        names = Name.query.filter_by(userID=u.id).order_by('score').all()
        f = SelectForm()
        f.name.choices = [(n.id, n.name) for n in names]
        if f.validate_on_submit():
            # this might be wonky, in ithacamusic it somehow understood the object from the id automatically??
            n = Name.query.get(f.name.data)
            n.score += 1
            if current_user.is_active:
                suggester = current_user
            else:
                suggester = None
                session['visited'].append(u.username)
            v = Vote(n, u, suggester)
            db.session.add(v)
            db.session.commit()
            return redirect(url_for("index"))
    return render_template("index.html", form=f, user=u)


def create_session():
    if 'visited' not in session.keys():
        session['visited'] = list()


def delete_name_by_id(name_id):
    name = Name.query.get(name_id)
    votes_to_delete = Vote.query.filter_by(nameID=name_id)
    for v in votes_to_delete:
        db.session.delete(v)
    suggester = name.suggester
    db.session.delete(name)
    db.session.commit()
    return suggester


# THE VIEWS

@app.route('/signin', methods=('GET', 'POST'))
def signin():
    if current_user.is_active:
        flash("You are already signed in.")
        return redirect(url_for("index"))
    signup = SignUpForm()
    login = LoginForm()
    if login.validate_on_submit():
        username = login.username.data
        password = login.password.data
        u = User.query.filter_by(username=username).first()
        if u:
            if pwd_context.verify(password, u.password):
                login_user(u)
                flash("You're in.")
                # FIXME: the first profile you vote on goes towards yourself for some reason
                return redirect(url_for("index"))
            else:
                flash("Wrong password.")
        else:
            # FIXME: this message pops up when you sign up correctly
            flash('Never heard of you.')
    if signup.validate_on_submit():
        username = signup.username.data
        password = pwd_context.encrypt(signup.password.data)
        about = signup.about.data
        url = signup.url.data
        badu = User.query.filter_by(username=username).first()
        if not badu:
            u = User(username, password, url, about)
            db.session.add(u)
            db.session.commit()
            login_user(u)
            flash("Welcome.")
            return redirect(url_for("index"))
        else:
            flash("Sorry, that one's taken.")
    return render_template("signin.html", signup=signup, login=login)


@app.route('/', methods=('GET', 'POST'))
def index():
    create_session()
    users = list(User.query.all())
    while users:
        u = random.choice(users)
        if (current_user.is_active and Vote.query.filter_by(voterID=current_user.id, userID=u.id).first())\
                or (current_user.is_anonymous and u.username in session['visited']):
            users.remove(u)
        else:
            return public_logged_in(u)
    return render_template("error.html", message="Either you have voted for every user on the website or a table got "
                                                 "dropped. If it's the former, thanks! If it's the latter, please do "
                                                 "not hold it against me. I am but a simple college student.")


# Don't develop this until you know how to make sure the same user doesn't vote a million times.
@app.route('/<name>', methods=('GET', 'POST'))
def public_profile(name):
    user = User.query.filter_by(username=name).first()
    if not user:
        # This message literally shows up on every page??? make it stop?????????????/
        # flash("User not found.")
        return redirect(url_for("index"))
    elif user != current_user:
        if Vote.query.filter_by(userID=user.id, voterID=current_user.id).first():
                flash("You've already voted on that user's name. Two votes is... too much power, don't you think?")
                return redirect(url_for("index"))

    return public_logged_in(user)


@app.route('/profile', methods=('GET', 'POST'))
@login_required
def private_profile():
    s = SignUpForm()
    # current_user is a copy, find the original
    user = User.query.get(current_user.id)
    s.username.data = user.username
    s.about.data = user.about
    s.url.data = user.photo_url
    names = Name.query.filter_by(userID=user.id).all()
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
    return render_template("profile.html", signupform=s, names=names)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You've successfully logged out.")
    return redirect(url_for("index"))


@app.route("/delete_account")
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

@app.route("/_toggle_suggestions")
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


@app.route("/_delete-<int:name_id>")
@login_required
def delete_name(name_id):
    delete_name_by_id(name_id)
    return jsonify(id=name_id)


@app.route("/_report-<int:name_id>")
@login_required
def report_name(name_id):
    reported = delete_name_by_id(name_id)
    is_active = False
    if reported:
        reported.flags += 1
        if reported.flags >= 3:
            reported.is_active = False
        is_active = True
    db.session.commit()
    return jsonify(id=name_id, active=is_active)
