from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, ValidationError, Email

from flask_mottak.models import Dataleveranse


class SelectLeverandorForm(FlaskForm):
    kort_lev = SelectField('Velg dataleverandør',  validate_choice=False)

    submit = SubmitField('Velg dataleverandør')


class SelectLeveranseForm(FlaskForm):
    kort_lev = StringField('Kortnavn dataleverandør', validators=[DataRequired()])
    leveranse = SelectField('Dataleveranse',  validate_choice=False)

    submit = SubmitField('Oppdater eksisterende dataleveranse')


class RegistrationForm(FlaskForm):
    leveranse = StringField('Dataleveranse', validators=[DataRequired(), Length(min=3, max=100)])
    kort_lev = StringField('Kortnavn dataleverandør', validators=[DataRequired()])
    mot_seksjon = StringField('Mottakende seksjon', validators=[DataRequired(), Length(min=0,max=4)])
    kontakt_seksjon = StringField('Kontakt mottakende seksjon', validators=[Length(max=200)])
    kontaktinfo_seksjon = StringField('Kontaktinfo mottakende seksjon', validators=[DataRequired(), Email()])
    kontakt_lev = StringField('Kontakt hos dataleverandør', validators=[Length(max=200)])
    kontaktinfo_lev = StringField('Kontaktinfo hos dataleverandør', validators=[DataRequired(), Email()])
    forventet_dato_neste = StringField('Forventet mottaksdato neste leveranse', validators=[Length(max=50)])
    hyppighet = StringField('Hyppighet', validators=[Length(max=50)])


    submit = SubmitField('Registrer dataleveranse')


    def validate_leveranse(self, leveranse):
        leveranse = Dataleveranse.query.filter_by(leveranse=leveranse.data).first()

        if leveranse:
            raise ValidationError(f'Dataleveranse er allerede registrert. Dataleveranse er knyttet til kortnavnet {leveranse.kort_lev}')


class UpdateDataleveranseForm(FlaskForm):
    leveranse = StringField('Dataleveranse', validators=[DataRequired(), Length(min=3, max=100)])
    kort_lev = StringField('Kortnavn dataleverandør', validators=[DataRequired()])
    mot_seksjon = StringField('Mottakende seksjon', validators=[DataRequired(), Length(min=0, max=4)])
    kontakt_seksjon = StringField('Kontakt mottakende seksjon', validators=[Length(max=200)])
    kontaktinfo_seksjon = StringField('Kontaktinfo mottakende seksjon', validators=[DataRequired(), Email()])
    kontakt_lev = StringField('Kontakt hos dataleverandør', validators=[Length(max=200)])
    kontaktinfo_lev = StringField('Kontaktinfo hos dataleverandør', validators=[DataRequired(), Email()])
    forventet_dato_neste = StringField('Forventet mottaksdato neste leveranse', validators=[Length(max=50)])
    hyppighet = StringField('Hyppighet', validators=[Length(max=50)])

    submit = SubmitField('Oppdater')