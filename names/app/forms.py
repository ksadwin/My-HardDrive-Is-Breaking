from flask.ext.wtf import Form
from wtforms import StringField, SelectField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired


class LoginForm(Form):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class SignUpForm(Form):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    about = TextAreaField("About", description="Anything you'd like people to know about you? Gender, age, last name, "
                                               "what the first letter should be, etc.")
    url = StringField("Photo", description="Paste the URL of the photo you'd like to use. (I am but a simple college "
                                           "student, I do not want to host your photos.)", validators=[DataRequired()])
    submit = SubmitField("Submit")


class SuggestForm(Form):
    name = StringField("Name", description="Type the name that comes to mind.", validators=[DataRequired()])
    submit = SubmitField("Submit")


class SelectForm(Form):
    name = SelectField("Name", description="Pick your favorite name.", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Submit")


