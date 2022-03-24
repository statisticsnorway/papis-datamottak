from flask import Blueprint
from flask import render_template, redirect, url_for, flash, request
from flask_mottak.models import Leverandor
from flask_mottak.leverandorer.forms import RegistrationForm, UpdateLeverandorForm
from flask_mottak import db


leverandorer = Blueprint('leverandorer', __name__)


@leverandorer.route('/leverandor', methods=['POST', 'GET'])
def register():
    #if current_user.is_authenticated:
    #    return redirect(url_for('main.index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        lev = Leverandor(kort_lev=form.kort_lev.data, leverandor=form.leverandor.data, websak=form.websak.data, ansv_seksjon=form.ansv_seksjon.data)
        db.session.add(lev)
        db.session.commit()
        flash(f'Leverandør opprettet for {form.leverandor.data}!', 'success')
        return redirect(url_for('leverandorer.view'))

    return render_template('leverandor.html', title='Registrer', form=form, legend='Registrer leverandør')

@leverandorer.route('/leverandor/<string:kort_lev>/update', methods=['POST', 'GET'])
def update_leverandor(kort_lev):
    # Vurdere å legge inn feilmelding slik: User.query.filter_by(username=username).first_or_404(description='There is no data with {}'.format(username))
    lev = Leverandor.query.filter_by(kort_lev=kort_lev).first_or_404(description=f'Ingen dataleverandør knyttet til {kort_lev}')
    alle_kortnavn = [kn.kort_lev for kn in db.session.query(Leverandor.kort_lev).all()]
    alle_kortnavn.remove(lev.kort_lev)
    alle_leverandorer = [l.leverandor for l in db.session.query(Leverandor.leverandor).all()]
    alle_leverandorer.remove(lev.leverandor)

    form = UpdateLeverandorForm()
    if form.validate_on_submit():
        if form.kort_lev.data in alle_kortnavn and form.leverandor.data in alle_leverandorer:
            lev_reg = Leverandor.query.get_or_404(form.kort_lev.data)
            flash(f'{form.kort_lev.data} er allerede registrert. Kortnavn er knyttet til dataleverandøren {lev_reg.leverandor}', 'warning')
            flash(f'{form.leverandor.data} er allerede registrert. Leverandør er knyttet til kortnavnet {lev_reg.kort_lev}','warning')
            return redirect(url_for('leverandorer.update_leverandor', kort_lev=lev.kort_lev))
        elif form.kort_lev.data in alle_kortnavn and form.leverandor.data not in alle_leverandorer:
            lev_reg = Leverandor.query.get_or_404(form.kort_lev.data)
            flash(f'{form.kort_lev.data} er allerede registrert. Kortnavn er knyttet til dataleverandøren {lev_reg.leverandor}', 'warning')
            return redirect(url_for('leverandorer.update_leverandor', kort_lev=lev.kort_lev))
        elif form.leverandor.data in alle_leverandorer and form.kort_lev.data not in alle_kortnavn:
            lev_reg = Leverandor.query.first_or_404(form.leverandor.data)
            flash(f'{form.leverandor.data} er allerede registrert. Leverandør er knyttet til kortnavnet {lev_reg.kort_lev}','warning')
            return redirect(url_for('leverandorer.update_leverandor', kort_lev=lev.kort_lev))
        else:
            lev.kort_lev = form.kort_lev.data
            lev.leverandor = form.leverandor.data
            lev.websak = form.websak.data
            lev.ansv_seksjon = form.ansv_seksjon.data
            db.session.commit()
            flash(f'Dataleverandør oppdatert for {form.leverandor.data}!', 'success')
            return redirect(url_for('leverandorer.view'))

    elif request.method == 'GET':
        form.kort_lev.data = lev.kort_lev
        form.leverandor.data = lev.leverandor
        form.websak.data = lev.websak
        form.ansv_seksjon.data = lev.ansv_seksjon

    return render_template('leverandor.html', title='Oppdater informasjon om dataleverandør',
                           form=form, legend='Oppdater informasjon om dataleverandør')



@leverandorer.route('/view')
def view():
    page = request.args.get('page', 1, type=int)
    leverandorer = Leverandor.query.order_by(Leverandor.kort_lev.desc()).paginate(page=page, per_page=2)

    #return render_template('view.html', title='Leverandører')
    return render_template('view.html', leverandorer=leverandorer, title='Leverandører')
