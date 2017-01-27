from flask_wtf import FlaskForm as Form
from wtforms import RadioField, BooleanField, SubmitField

class ColorSelect(Form):
     active_color  = BooleanField("BLUE", default=True)
     submit = SubmitField('START')
