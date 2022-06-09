from flask import Blueprint
from flask import render_template, redirect, url_for, flash, request
from flask_mottak.models import Dataleveranse, Leverandor, Periodeleveranse
from flask_mottak.periodeleveranser.forms import RegistrationForm, UpdatePeriodeleveranseForm, SelectLeverandorForm, \
    SelectLeveranseForm, SelectPeriodeForm
from flask_mottak import db


periodeleveranser = Blueprint('periodeleveranser', __name__)


@periodeleveranser.route('/velg_leverandor', methods=['POST', 'GET'])
def velg_leverandor():
    alle_kortnavn = [kn.kort_lev for kn in db.session.query(Leverandor.kort_lev).all()]

    form = SelectLeverandorForm()
    form.kort_lev.choices = [kn for kn in alle_kortnavn]

    if form.validate_on_submit():
        kort_lev = form.kort_lev.data

        return redirect(url_for('periodeleveranser.velg_leveranse', kort_lev=kort_lev))

    return render_template('velg_dataleverandor.html', title='Registrer periodeleveranse', form=form, legend='Registrer periodeleveranse')


@periodeleveranser.route('/velg_periodeleveranse/<string:kort_lev>', methods=['POST', 'GET'])
def velg_leveranse(kort_lev):
    leveranser = Dataleveranse.query.filter_by(kort_lev=kort_lev).all()
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

        return redirect(url_for('periodeleveranser.velg_periodeleveranse', kort_lev=kort_lev, leveranse=leveranse))

    elif request.method == 'GET':
        form.kort_lev.data = kort_lev
        form.kort_lev(disabled=True)


    return render_template('velg_dataleveranse.html', title='Dataleveranse', form=form, leveranse=min_leverandor, legend='Registrer periodeleveranse')


@periodeleveranser.route('/velg_periodeleveranse/<string:kort_lev>/<string:leveranse>', methods=['POST', 'GET'])
def velg_periodeleveranse(kort_lev, leveranse):
    periodeleveranser = Periodeleveranse.query.filter_by(leveranse=leveranse)
    alle_periodeleveranser = [pl.periode for pl in periodeleveranser]

    form = SelectPeriodeForm()
    form.periode.choices = [plv for plv in alle_periodeleveranser]
    if len(alle_periodeleveranser) == 0:
        flash(f'Ingen periodeleveranse er knyttet til dataleveransen {leveranse}', 'info')

    if form.validate_on_submit():
        leveranse = form.leveranse.data
        periode = form.periode.data
        kort_lev = form.kort_lev.data

        return redirect(url_for('periodeleveranser.update_leveranse', leveranse=leveranse, periode=periode, kort_lev=kort_lev))

    elif request.method == 'GET':
        form.kort_lev.data = kort_lev
        form.kort_lev(disabled=True)
        form.leveranse.data = leveranse
        form.leveranse(disabled=True)

    return render_template('velg_periodeleveranse.html', title='Periodeleveranse', form=form, kort_lev=kort_lev, dataleveranse=leveranse, legend='Registrer periodeleveranse')




@periodeleveranser.route('/periodeleveranse/<string:kort_lev>/<string:dataleveranse>', methods=['POST', 'GET'])
def register(kort_lev, dataleveranse):
    form = RegistrationForm()

    if form.validate_on_submit():
        periode = Periodeleveranse(periode=form.periode.data, leveranse=form.leveranse.data,
                                   kort_lev=form.kort_lev.data)
        db.session.add(periode)
        db.session.commit()
        flash(f'Periode opprettet for {form.kort_lev.data} - {form.leveranse.data}!', 'success')
        return redirect(url_for('leverandorer.view'))#View bør flyttes til main?!

    elif request.method == 'GET':
        form.leveranse.data = dataleveranse
        form.leveranse(disabled=True)
        form.kort_lev.data = kort_lev
        form.kort_lev(disabled=True)

    return render_template('periodeleveranse.html', title='Registrer', form=form, legend='Registrer periodeleveranse')


@periodeleveranser.route('/periodeleveranse/<string:periode>/<string:leveranse>/<string:kort_lev>/update', methods=['POST', 'GET'])
def update_leveranse(periode, leveranse, kort_lev):
    perioden = Periodeleveranse.query.get([periode, leveranse, kort_lev])

    periodeleveranser = Periodeleveranse.query.filter_by(leveranse=leveranse)
    alle_periodeleveranser = [pl.periode for pl in periodeleveranser]

    periodeleveransen = ''
    andre_periodeleveranser = []
    for pl in alle_periodeleveranser:
        if pl == periode:
            periodeleveransen = pl
        else:
            andre_periodeleveranser.append(pl)

    form = UpdatePeriodeleveranseForm()
    form.periode.choices = [plv for plv in alle_periodeleveranser]

    print("periode før update, ", perioden)
    if form.validate_on_submit():
        print("perioden", perioden)
        perioden.periode = form.periode.data
        #perioden.data_leveranse = form.leveranse.data
        #perioden.kort_lev = form.kort_lev.data

        for pl in andre_periodeleveranser:
            if pl == form.periode.data:
                flash(f'Periode er allerede registrert på denne dataleveransen- {leveranse}', 'warning')
                return redirect(url_for('periodeleveranser.update_leveranse', leveranse=leveranse, periode=periode, kort_lev=kort_lev))

        db.session.commit()
        flash(f'Periodeleveranse oppdatert for: {form.leveranse.data} - {form.periode.data}!', 'success')
        return redirect(url_for('leverandorer.view'))

    elif request.method == 'GET':
        form.periode.data = periode
        form.leveranse.data = leveranse
        form.kort_lev.data = kort_lev

    return render_template('periodeleveranse.html', title='Oppdater informasjon om periodeleveranse',
                           form=form, legend='Oppdater informasjon om periodeleveranse')


