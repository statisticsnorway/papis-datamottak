from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired, Length, ValidationError

from flask_mottak.models import Leverandor, Dataleveranse


class RegistrationForm(FlaskForm):
    kort_lev = StringField('Kortnavn dataleverandør', validators=[DataRequired(), Length(min=3,max=6)])
    leverandor = StringField('Navn på dataleverandør', validators=[DataRequired(), Length(min=3,max=100)])
    websak = StringField('Websak', validators=[Length(max=200)])
    ansv_seksjon = StringField('Ansvarlig seksjon for avtale', validators=[Length(min=0,max=4)])

    submit = SubmitField('Registrer')

    def validate_kort_lev(self, kort_lev):
        kort_lev = Leverandor.query.filter_by(kort_lev=kort_lev.data).first()

        if kort_lev:
            raise ValidationError(f'Kortnavn på dataleverandør er allerede registrert. Kortnavn er knyttet til dataleverandøren {kort_lev.leverandor}')

    def validate_leverandor(self, leverandor):
        leverandor = Leverandor.query.filter_by(leverandor=leverandor.data).first()

        if leverandor:
            raise ValidationError(f'Dataleverandør er allerede registrert. Dataleverandør er knyttet til kortnavnet {leverandor.kort_lev}')


class UpdateLeverandorForm(FlaskForm):
    kort_lev = StringField('Kortnavn dataleverandør', validators=[DataRequired(), Length(min=3,max=6)])
    leverandor = StringField('Navn på dataleverandør', validators=[DataRequired(), Length(min=3,max=100)])
    websak = StringField('Websak', validators=[Length(max=200)])
    ansv_seksjon = StringField('Ansvarlig seksjon for avtale', validators=[Length(min=0,max=4)])

    submit = SubmitField('Oppdater')
