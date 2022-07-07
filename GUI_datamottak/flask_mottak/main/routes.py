from flask import Blueprint
from flask import request, redirect, render_template, flash, url_for, current_app, g
from flask_mottak.models import Leverandor
from flask_mottak.leverandorer.forms import SelectLeverandorForm
from flask_mottak import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/pseudo')
def pseudo():
    g.header = ('Gammelt filnavn', 'Nytt filnavn', 'Pseudo kolonner', 'Filtype')
    future = [(x[0], x[1], x[2], x[3]) for x in current_app.pseudoService.worklistFuture]
    g.toDo = current_app.pseudoService.showList()
    g.errorHeader = ('Gammelt filnavn', 'Nytt filnavn', 'Pseudo kolonner', 'Error melding')
    g.error = current_app.pseudoService.error
    g.done = current_app.pseudoService.done
    g.tables = [('Future list', g.header, future),
                ('Done list:', g.header, g.done),
                ('Error list:', g.errorHeader, g.error)]

    return render_template('pseudo.html')



@main.route('/search', methods=['POST', 'GET'])
def search():
    #alle_kortnavn = [kn.kort_lev for kn in db.session.query(Leverandor.kort_lev).all()]

    #form = SelectLeverandorForm()
    #form.kort_lev.choices = [kn for kn in alle_kortnavn]

    #if form.validate_on_submit():
    #    kort_lev = form.kort_lev.data

   #     return redirect(url_for('dataleveranser.velg_leveranse', kort_lev=kort_lev))

    if request.method == 'POST':
      kortnavn = request.form['folder']
      kort_lev = Leverandor.query.filter_by(kort_lev=kortnavn).first()
      if kort_lev:
        return redirect(url_for('leverandorer.update_leverandor', kort_lev=kortnavn))
      else:
          flash(f'{kortnavn} er ikke registrert. Legg inn kortnavn på ny eller registrer ny leverandør her', 'warning')
          return redirect(url_for('leverandorer.register'))
