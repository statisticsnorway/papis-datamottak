from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField, IntegerField, SelectMultipleField, DateField
from wtforms.validators import DataRequired, Length, ValidationError, InputRequired, NumberRange
from flask_mottak.models import Fil
import datetime


class SelectLeverandorForm(FlaskForm):
    kort_lev = SelectField('Velg dataleverandør',  validate_choice=False)

    submit = SubmitField('Velg dataleverandør')


class SelectLeveranseForm(FlaskForm):
    kort_lev = StringField('Kortnavn dataleverandør', validators=[DataRequired()])
    leveranse = SelectField('Dataleveranse',  validate_choice=False)

    submit = SubmitField('Velg dataleveranse')


class SelectPeriodeForm(FlaskForm):
    kort_lev = StringField('Kortnavn dataleverandør', validators=[DataRequired()])
    leveranse = StringField('Dataleveranse', validators=[DataRequired()])
    periode = SelectField('Periode', validate_choice=False)

    submit = SubmitField('Velg periodeleveranse')



class RegistrerFilSkjema(FlaskForm):
    periode = StringField('Periode', validators=[DataRequired(), Length(max=20)])
    data_leveranse = StringField('Dataleveranse', validators=[DataRequired(), Length(max=100)])
    kort_lev = StringField('Kortnavn dataleverandør', validators=[DataRequired(), Length(min=0, max=6)])
    filnavn = StringField('Filnavn', validators=[DataRequired(), Length(max=200)])
    fil_mottatt = DateField('Mottaksdato (DD-MM-ÅÅÅÅ)', validators=[InputRequired()])# format='%d-%m-%Y',

    submit = SubmitField('Opprett fil')

    def validate_filnavn(self, filnavn):
        filnavn = Fil.query.filter_by(filnavn=filnavn.data).first()

        if filnavn:
            raise ValidationError(f'Filnavn er allerede registrert.')


    def validate_fil_mottatt(self, fil_mottatt):

        if fil_mottatt.data < datetime.date.today():#, '%d-%m-%Y'
            raise ValidationError("Dato kan ikke være i fortiden!")




class Konfigurasjon_mFnrLeting(FlaskForm):
    pseudo_vars = SelectMultipleField('Vaiable for pseudonymisering')
    fodselsnr = SelectField('Fødselsnummer (for leting)', validate_choice=False)
    fornavn = SelectField('Fornavn',  validate_choice=False)
    mellomnavn = SelectField('Mellomnavn',  validate_choice=False)
    etternavn = SelectField('Etternavn',  validate_choice=False)
    fra_alder = IntegerField('Fra alder', validators=[DataRequired(), NumberRange(min=0, max=120)])
    til_alder = IntegerField('Til alder', validators=[DataRequired(), NumberRange(min=0, max=120)])
    tidbef = StringField('Tidsangivelse for befolkningsfil', validators=[DataRequired(), Length(max=100)])
    sep = StringField('Seperator', validators=[Length(max=1)])
    header = SelectField('Header', choices=['1', '0'], validators=[InputRequired()], coerce=str)
    innlprog = StringField('Innlesingsprogram', validators=[Length(max=200)])
    bruk_navn = StringField('Navn på utfil', validators=[DataRequired(), Length(max=100)])
    filstamme = StringField('Filstamme', validators=[DataRequired(), Length(max=100)])

    submit = SubmitField('Oppdater konfigurasjonsfil')


class Konfigurasjon_uFnrLeting(FlaskForm):
    pseudo_vars = SelectMultipleField('Vaiable for pseudonymisering')
    fodselsnr =  SelectField('Fødselsnummer (for kontroll)', validate_choice=False)
    sep = StringField('Seperator', validators=[Length(max=1)])
    header = SelectField('Header', choices=['1', '0'], validators=[InputRequired()], coerce=str)
    innlprog = StringField('Innlesingsprogram', validators=[Length(max=200)])
    bruk_navn = StringField('Navn på utfil', validators=[DataRequired(), Length(max=100)])
    filstamme = StringField('Filstamme', validators=[DataRequired(), Length(max=100)])

    submit = SubmitField('Oppdater konfigurasjonsfil')



class fnrLeting(FlaskForm):
    fnrleting = SelectField('Fnrleting', choices=['Ja', 'Nei'], validators=[InputRequired()], coerce=str)

    submit = SubmitField('Gå')