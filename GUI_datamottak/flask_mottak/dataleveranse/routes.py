from flask import Blueprint
from flask import render_template, redirect, url_for, flash, request
from flask_mottak.models import Dataleveranse, Leverandor
from flask_mottak.dataleveranse.forms import RegistrationForm, UpdateDataleveranseForm, SelectLeverandorForm, SelectLeveranseForm
from flask_mottak import db


dataleveranser = Blueprint('dataleveranser', __name__)


@dataleveranser.route('/velg_dataleverandor', methods=['POST', 'GET'])
def velg_leverandor():
    alle_kortnavn = [kn.kort_lev for kn in db.session.query(Leverandor.kort_lev).all()]

    form = SelectLeverandorForm()
    form.kort_lev.choices = [kn for kn in alle_kortnavn]

    if form.validate_on_submit():
        kort_lev = form.kort_lev.data

        return redirect(url_for('dataleveranser.velg_leveranse', kort_lev=kort_lev))

    return render_template('velg_dataleverandor.html', title='Registrer dataleveranse', form=form, legend='Registrer dataleveranse')


@dataleveranser.route('/velg_dataleveranse/<string:kort_lev>', methods=['POST', 'GET'])
def velg_leveranse(kort_lev):
    leveranser = Dataleveranse.query.filter_by(leverandor_kort_lev=kort_lev).all()
    alle_leveranser = [lev.leveranse for lev in leveranser]
    leverandor = Leverandor.query.get(kort_lev)
    min_leverandor = leverandor.kort_lev

    form = SelectLeveranseForm()
    form.leveranse.choices = [lev for lev in alle_leveranser]
    if len(alle_leveranser) == 0:
        flash(f'Ingen dataleveranse er knyttet til dataleverandøren {kort_lev}', 'info')

    if form.validate_on_submit():
        kort_lev = form.kort_lev.data
        leveranse = form.leveranse.data

        return redirect(url_for('dataleveranser.update_leveranse', kort_lev=kort_lev, leveranse=leveranse))

    elif request.method == 'GET':
        form.kort_lev.data = kort_lev
        form.kort_lev(disabled=True)


    return render_template('velg_dataleveranse.html', title='Dataleveranse', form=form, leveranse=min_leverandor, legend='Registrer dataleveranse')



@dataleveranser.route('/dataleveranse/<string:kort_lev>', methods=['POST', 'GET'])
def register(kort_lev):
    form = RegistrationForm()

    if form.validate_on_submit():
        leverandor = Leverandor.query.get(kort_lev)
        min_leverandor = leverandor.kort_lev
        leveranse = Dataleveranse(leveranse=form.leveranse.data, leverandor_kort_lev=min_leverandor,
                                  mot_seksjon=form.mot_seksjon.data,
                                  kontakt_seksjon=form.kontakt_seksjon.data, kontaktinfo_seksjon=form.kontaktinfo_seksjon.data,
                                  kontakt_lev=form.kontakt_lev.data, kontaktinfo_lev=form.kontaktinfo_lev.data,
                                  forventet_dato_neste=form.forventet_dato_neste.data, hyppighet=form.hyppighet.data
                                  )
        db.session.add(leveranse)
        db.session.commit()
        flash(f'Leveranse opprettet for {form.leverandor_kort_lev.data}!', 'success')
        return redirect(url_for('leverandorer.view'))#View bør flyttes til main?!

    elif request.method == 'GET':
        form.leverandor_kort_lev.data = kort_lev
        form.leverandor_kort_lev(disabled=True)

    return render_template('dataleveranse.html', title='Registrer', form=form, legend='Registrer dataleveranse')

@dataleveranser.route('/dataleveranse/<string:leveranse>/<string:kort_lev>/update', methods=['POST', 'GET'])
def update_leveranse(kort_lev, leveranse):
    dataleveransen = Dataleveranse.query.get(leveranse)
    #dataleveranser = Dataleveranse.query.filter_by(leverandor_kort_lev=kort_lev).first_or_404(description=f'Ingen dataleveranse knyttet til {kort_lev}')
    #alle_kortnavn = [kn.leverandor_kort_lev for kn in db.session.query(Dataleveranse.leverandor_kort_lev).all()]
    #alle_kortnavn.remove(dataleveranser.leverandor_kort_lev)
    #alle_leveranser = [l.leveranse for l in db.session.query(Dataleveranse.leveranse).all()]
    #alle_leveranser.remove(dataleveranser.leveranse)

    form = UpdateDataleveranseForm()
    if form.validate_on_submit():
        leverandor = Leverandor.query.get(kort_lev)
        min_leverandor = leverandor.kort_lev

        dataleveransen.leveranse = leveranse
        dataleveransen.leverandor_kort_lev = min_leverandor
        dataleveransen.mot_seksjon = form.mot_seksjon.data
        dataleveransen.kontakt_seksjon = form.kontakt_seksjon.data
        dataleveransen.kontaktinfo_seksjon = form.kontaktinfo_seksjon.data
        dataleveransen.kontakt_lev = form.kontakt_lev.data
        dataleveransen.kontaktinfo_lev = form.kontaktinfo_lev.data
        dataleveransen.forventet_dato_neste = form.forventet_dato_neste.data
        dataleveransen.hyppighet = form.hyppighet.data

        db.session.commit()
        flash(f'Dataleveranse oppdatert for: {kort_lev} - {leveranse}!', 'success')
        return redirect(url_for('leverandorer.view'))

    elif request.method == 'GET':
        form.leverandor_kort_lev.data = kort_lev
        form.leveranse.data = leveranse
        form.mot_seksjon.data = dataleveransen.mot_seksjon
        form.kontakt_seksjon.data = dataleveransen.kontakt_seksjon
        form.kontaktinfo_seksjon.data = dataleveransen.kontaktinfo_seksjon
        form.kontakt_lev.data = dataleveransen.kontakt_lev
        form.kontaktinfo_lev.data = dataleveransen.kontaktinfo_lev
        form.forventet_dato_neste.data = dataleveransen.forventet_dato_neste
        form.hyppighet.data = dataleveransen.hyppighet

    return render_template('dataleveranse.html', title='Oppdater informasjon om dataleveranse',
                           form=form, legend='Oppdater informasjon om dataleveranse')


