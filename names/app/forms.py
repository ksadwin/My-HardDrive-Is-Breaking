from flask_wtf import Form
from wtforms import StringField, SelectField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired
# TODO: from flask_wtf.recaptcha import RecaptchaField


class LoginForm(Form):
    username_l = StringField("Username", validators=[DataRequired()])
    password_l = PasswordField("Password", validators=[DataRequired()])
    submit_l = SubmitField("Submit")


class SignUpForm(Form):
    username_s = StringField("Username", validators=[DataRequired()])
    password_s = PasswordField("Password", validators=[DataRequired()])
    about_s = TextAreaField("About", description="Anything you'd like people to know about you? Gender, age, last name,"
                                                 " what the first letter should be, etc.")
    # TODO: just removed the DataRequired() validator from url, make sure the world doesn't explode
    url_s = StringField("Photo", description="Paste the URL of the photo you'd like to use. (I am but a simple college "
                                             "student, I do not want to host your photos.)")
    submit_s = SubmitField("Submit")


class SuggestForm(Form):
    name = StringField("Name", description="Type the name that comes to mind.", validators=[DataRequired()])
    submit = SubmitField("Submit")


class SelectForm(Form):
    name = SelectField("Name", description="Pick your favorite name.", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Submit")


