from flask import Blueprint
from flask import request, render_template, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from flask_pseudo.models import Log

logs = Blueprint('logs', __name__)



@logs.route('/log', methods=['POST', 'GET'])   
@login_required
def log():
    page = request.args.get('page', 1, type=int)
    logs = Log.query.order_by(Log.dato_opprettet.desc()).paginate(page=page, per_page=2)
    
    return render_template('logs.html', logs = logs, title='Log')


