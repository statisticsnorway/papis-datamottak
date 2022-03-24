from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from flask_pseudo.models import User



class RegistrationForm(FlaskForm):
  username = StringField('Brukernavn', validators=[DataRequired(), Length(min=2,max=20)])
  password = PasswordField('Passord', validators=[DataRequired()])
  confirm_password = PasswordField('Bekreft Passord', validators=[DataRequired(), EqualTo('password')])
  submit = SubmitField('Registrer')
  
  def validate_username(self, username):
    user = User.query.filter_by(username=username.data).first()
    
    if user:
      raise ValidationError('Brukernavn er allerede brukt. Velg et annet.')
      

class LoginForm(FlaskForm):
  username = StringField('Brukernavn', validators=[DataRequired(), Length(min=2,max=20)])
  password = PasswordField('Passord', validators=[DataRequired()])
  remember = BooleanField('Remember me')
  submit = SubmitField('Logg inn')
