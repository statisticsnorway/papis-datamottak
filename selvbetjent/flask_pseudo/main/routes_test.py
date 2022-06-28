from flask import Blueprint, current_app, request, render_template, flash, g
testB = Blueprint('testBlueprint', __name__, template_folder="Templates_test")

@testB.before_app_first_request
def init_main():
    pass
    #if not hasattr(current_app, 'pseudoService'):
    #    raise AttributeError('no pseudoService set in main')
    #current_app.pseudoService.start()
    
#@testB.route('/pseudo')
#def pseudo():
#    return str((current_app.pseudoService.showList(), current_app.pseudoService.error))

@testB.route('/index', methods=['POST', 'GET'])
@testB.route('/', methods=['POST', 'GET'])
def index():
    #return render_template('index.html')
    g.header = ['fnr','navn']
    g.rows = [['12121212124',	'Randi Rekkverk'],
             ['12345678912',	'Audun Automat']]

    if hasattr(current_app, 'json_buffered'):
        g.json = current_app.json_buffered
    else:
        print('Making g.json')
        g.json = {'gammelfil': r'C:\Users\tir\Desktop\python\sas7bdat\testfil.cvs', 
                    'nyfil': r'C:\Users\tir\Desktop\python\sas7bdat\testfil_pseudo.cvs', 
                    'pseudoCol': [True, False], 'filetype': 'cvs'}
        current_app.json_buffered = g.json

    
    if request.method == 'GET':
        return render_template('dropbox.html')
    
    print(f'Request form: {request.form}')  
    
    for i in range(len(g.pseudo)):
        g.json['pseudoCol'][i] = (
            request.form.get(f'pseudo{i}') == 'on')
    
    if request.form.get('submit_button') == 'Oppdater konfigurasjon':
        flash('Oppdater konfigurasjonsfil', 'info')
    if request.form.get('submit_button') == 'Pseudonymiser fil':
        flash('Pseudonymiserer fil', 'info')
    if request.form.get('newFilename'):
        g.json['nyfil'] = request.form['newFilename']
        flash(f'Nytt filnavn:{g.json["nyfil"]}', 'info')
    return render_template('dropbox.html')



