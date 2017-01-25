from flask_wtf import FlaskForm as Form
from wtforms import RadioField, BooleanField, SubmitField

class ColorSelect(Form):
#    active_color  = RadioField('Select Color', choices=[
#        ('Red', 'Red'),
#        ('Blue', 'Blue')], default='Red')
     active_color  = BooleanField("RED", default=True)
     submit = SubmitField('START')
