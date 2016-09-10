from flask_wtf import Form
from wtforms import StringField, SelectField, SubmitField, PasswordField, TextAreaField, validators
# TODO: from flask_wtf.recaptcha import RecaptchaField


class LoginForm(Form):
    username_l = StringField("Username", validators=[validators.required()])
    password_l = PasswordField("Password", validators=[validators.required()])
    submit_l = SubmitField("Submit")


class SignUpForm(Form):
    username_s = StringField("Username", validators=[validators.required(), validators.length(min=4, max=32),
                                                     validators.regexp("[0-9A-Za-z_]+")],
                             description="Letters, numbers, and underscores only, please!")
    password_s = PasswordField("Password", validators=[validators.required(), validators.length(min=6, max=48)],
                               description="At least 6 characters. Maybe don't use the same password here as you use "
                                           "for, say, your online banking.")
    about_s = TextAreaField("About", description="Optional: Anything you'd like people to know about you? Gender, age, "
                                                 "last name, what the first letter should be, etc.")
    url_s = StringField("Photo", description="Optional: Paste the URL of the photo you'd like to use. (I am but a "
                                             "simple college student, I do not want to host your photos.)")
    submit_s = SubmitField("Submit")


class SuggestForm(Form):
    name = StringField("Name", description="Type the name that comes to mind.",
                       validators=[validators.required(), validators.length(max=32)])
    submit = SubmitField("Submit")


class SelectForm(Form):
    name = SelectField("Name", description="Pick your favorite name.", coerce=int, validators=[validators.required()])
    submit = SubmitField("Submit")


