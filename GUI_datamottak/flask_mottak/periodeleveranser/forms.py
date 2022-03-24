from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError, Email

from flask_mottak.models import Dataleveranse, Leverandor, Periodeleveranse


class SelectLeverandorForm(FlaskForm):
    kort_lev = SelectField('Velg dataleverandør',  validate_choice=False)

    submit = SubmitField('Velg dataleverandør')


class SelectLeveranseForm(FlaskForm):
    kort_lev = StringField('Kortnavn dataleverandør', validators=[DataRequired()])
    leveranse = SelectField('Dataleveranse',  validate_choice=False)

    submit = SubmitField('Hent dataleveranse')


class SelectPeriodeForm(FlaskForm):
    kort_lev = StringField('Kortnavn dataleverandør', validators=[DataRequired()])
    leveranse = StringField('Dataleveranse', validators=[DataRequired()])
    periode = SelectField('Periode', validate_choice=False)

    submit = SubmitField('Oppdater eksisterende periodeleveranse')

class RegistrationForm(FlaskForm):
    periode = StringField('Periode', validators=[DataRequired(), Length(max=20)])
    data_leveranse = StringField('Dataleveranse', validators=[DataRequired(), Length(max=100)])
    kort_lev = StringField('Kortnavn dataleverandør', validators=[DataRequired(), Length(min=0,max=6)])
    forventet_dato = StringField('Forventet mottaksdato', validators=[DataRequired(), Length(max=20)])
    mottatt_dato = StringField('Faktisk mottaksdato', validators=[DataRequired(), Length(max=20)])

    submit = SubmitField('Registrer periodeleveranse')


#    def validate_periode(self, periode):
#        periode = Periodeleveranse.query.filter_by(periode=periode.data).first()
#
#        if periode:
#            raise ValidationError(f'Periode er allerede registrert. Perioden er knyttet til dataleveransen {periode.data_leveranse}')


class UpdatePeriodeleveranseForm(FlaskForm):
    periode = StringField('Periode', validators=[DataRequired(), Length(max=20)])
    data_leveranse = StringField('Dataleveranse', validators=[DataRequired(), Length(max=100)])
    kort_lev = StringField('Kortnavn dataleverandør', validators=[DataRequired(), Length(min=0, max=6)])
    forventet_dato = StringField('Forventet mottaksdato', validators=[DataRequired(), Length(max=20)])
    mottatt_dato = StringField('Faktisk mottaksdato', validators=[DataRequired(), Length(max=20)])

    submit = SubmitField('Oppdater')
