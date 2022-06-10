from flask import Blueprint
from flask import request, current_app
from flask_login import current_user, login_required


dev = Blueprint('development',__name__)

@dev.route('/shutdown', methods=['GET', 'POST'])
def shutdown():
    if hasattr(current_app, 'pseudoService'):
        current_app.pseudoService.shutdown()
    shutdown_server()
    return 'Server shutting down...'

@dev.route('/app/')
@dev.route('/app/<variable>')
def app_looker(variable = None):
    if variable == None or variable == '' or not getattr(current_app, variable, None):
        string = str([('Key:',key, 'Type:', 
                       getattr(type(val),'__name__', 'NoName'), 'Val:', val)
                 for key, val in vars(current_app).items()])
    else:
        string = str([('Key:',key, 'Type:', type(val), 'Val:', val)
                 for key, val in vars(getattr(current_app, variable)).items()])
    return f'Variable: {variable}, Result: {string}'

@dev.route('/use/')
@dev.route('/use/<variable>')
@login_required
def user_looker(variable = None):
    if variable == None or variable == '' or not getattr(current_user, variable, None):
        string = str([('Key:',key, 'Type:', 
                       getattr(type(val),'__name__', 'NoName'), 'Val:', val)
                 for key, val in vars(current_user).items()])
    else:
        string = str([('Key:',key, 'Type:', type(val), 'Val:', val)
                 for key, val in vars(getattr(current_app, variable)).items()])
    return f'Variable: {variable}, Result: {string}'

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
