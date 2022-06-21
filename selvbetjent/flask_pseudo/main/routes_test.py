from flask import Blueprint, current_app, request, render_template, flash, g
testB = Blueprint('testBlueprint', __name__, template_folder="Templates_test")

@testB.before_app_first_request
def init_main():
    if not hasattr(current_app, 'pseudoService'):
        raise AttributeError('no pseudoService set in main')
    current_app.pseudoService.start()
    
@testB.route('/pseudo')
def pseudo():
    return str((current_app.pseudoService.showList(), current_app.pseudoService.error))

@testB.route('/index', methods=['POST', 'GET'])
@testB.route('/', methods=['POST', 'GET'])
def index():
    #return render_template('index.html')
    g.header = ['fnr','navn']
    g.row0 = ['12121212124',	'Randi Rekkverk']
    g.row1 = ['12345678912',	'Audun Automat']
        
    g.jsonfile = {'gammelfil': r'C:\Users\tir\Desktop\python\sas7bdat\testfil.cvs', 
                    'nyfil': r'C:\Users\tir\Desktop\python\sas7bdat\testfil_pseudo.cvs', 
                    'pseudoCol': [], 'filetype': 'cvs'}

    if request.method == 'GET':
        return render_template('dropbox.html')
    elif request.method != 'POST':
        return 'Request method not GET or POST'
    
    if request.form['submit_button'] == 'Oppdater konfigurasjonsfil':
        flash('Oppdater konfigurasjonsfil', 'info')
    elif request.form['submit_button'] == 'Pseudonymiser fil':
        flash('Pseudonymiserer fil', 'info')
    else:
        return "Should not be reached"
    return render_template('dropbox.html')

@testB.route('/files/', methods=['POST', 'GET'])
@testB.route('/files/<path:path>', methods=['POST', 'GET'])
def files(path = ''):
    return showFile(current_app.pseudoService)

def showFile(pseudoService):
    g.header = ['fnr','navn']
    g.row0 = ['12121212124',	'Randi Rekkverk']
    g.row1 = ['12345678912',	'Audun Automat']
    
        
    g.jsonfile = {'gammelfil': r'C:\Users\tir\Desktop\python\sas7bdat\testfil.cvs', 
                    'nyfil': r'C:\Users\tir\Desktop\python\sas7bdat\testfil_pseudo.cvs', 
                    'pseudoCol': [], 'filetype': 'cvs'}
    g.orgfile = g.jsonfile['gammelfil']
    g.newfile = g.jsonfile['nyfil']

    if request.method == 'GET':
        return render_template('dropbox.html')
    elif request.method != 'POST':
        return 'Request method not GET or POST'
    
    #g.jsonfile['pseudo'] = request.form.getlist('pseudo')
    #jsonfile['nyttfilnavn'] = request.form.get('nyttnavn')
    
    if request.form['submit_button'] == 'Oppdater konfigurasjonsfil':
        flash('Oppdater konfigurasjonsfil', 'info')
    elif request.form['submit_button'] == 'Pseudonymiser fil':
        flash('Pseudonymiserer fil', 'info')
        pseudoService.add(g.jsonfile, None)
        #return redirect(url_for('main.pseudo'))
    else:
        return "Should not be reached"
    #varsx = sas_op.getVarnames(sas_op.getFilename(filename), sas_op.getPath(filename))
    #columns = varsx.iloc[:,0].to_list()
    return render_template('dropbox.html')

