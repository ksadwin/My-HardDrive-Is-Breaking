from flask_wtf import Form
from wtforms import StringField, SubmitField, IntegerField, validators


class TagForm(Form):
    username = StringField("Tumblr username: ", validators=[validators.required(), validators.length(max=32)])
    height = IntegerField("Height: ", default=300)
    width = IntegerField("Width: ", default=200)
    color = StringField("Text color (hex): #", default="ffffff", validators=[validators.regexp("[0-9A-Fa-f]{6}")])
    submit = SubmitField("Submit")
