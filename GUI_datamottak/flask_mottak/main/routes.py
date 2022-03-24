from flask import Blueprint
from flask import request, redirect, render_template, flash, url_for
from flask_mottak.models import Leverandor

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')



@main.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
      kortnavn = request.form['folder']
      kort_lev = Leverandor.query.filter_by(kort_lev=kortnavn).first()
      if kort_lev:
        return redirect(url_for('leverandorer.update_leverandor', kort_lev=kortnavn))
      else:
          flash(f'{kortnavn} er ikke registrert. Legg inn kortnavn på ny eller registrer ny leverandør her', 'warning')
          return redirect(url_for('leverandorer.register'))
