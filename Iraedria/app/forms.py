from flask_wtf import Form
from wtforms import StringField, SubmitField, IntegerField, PasswordField, validators


class TagForm(Form):
    username = StringField("Tumblr username: ", validators=[validators.required(), validators.length(max=32)])
    height = IntegerField("Height: ", default=200)
    width = IntegerField("Width: ", default=300)
    color = StringField("Text color (hex): #", default="ffffff", validators=[validators.regexp("[0-9A-Fa-f]{6}")])
    submit = SubmitField("Submit")


class PhotoForm(Form):
    urls_to_add = StringField("URLs", description="comma separated, no spaces", validators=[validators.required()])
    password = PasswordField("Secret", validators=[validators.required(), validators.length(min=18, max=32)])
    submit = SubmitField("Submit")
