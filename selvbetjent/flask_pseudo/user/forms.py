from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField
#from wtforms import BooleanField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
  username = StringField('Brukernavn', validators=[DataRequired(), Length(min=2,max=40)])
  password = PasswordField('Passord', validators=[DataRequired()])
  #remember = BooleanField('Remember me')
  submit = SubmitField('Logg inn')
