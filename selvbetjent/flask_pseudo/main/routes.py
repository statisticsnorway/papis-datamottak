from flask import Blueprint
from flask import request, redirect, render_template, json, flash, url_for, current_app
from flask_login import current_user, logout_user
from ..models import Log
from ..create_app import data, db, root
from stat import S_ISDIR, S_ISREG
from os.path import split 
import os
import io
from urllib.parse import quote
import pandas as pd
import threading

main = Blueprint('main', __name__)

#sas_op = SAS_Operasjoner()

@main.before_app_first_request
def init_main():
    current_app.data = data
    current_app.db = db
    current_app.root = root

@main.route('/index')
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
      path = request.form['folder']
      return redirect(url_for('main.files', path=path))
    else:
      flash('Oppgi stammekatalog</fil>', 'warning')
      
def con_is_active(ssh):
    if ssh.get_transport() is not None:
        if False == ssh.get_transport().is_active():
            return False
    try:
        ssh.get_transport().send_ignore()
        return True
    except EOFError:
        return False

@main.route('/files/')
@main.route('/files/<path:path>', methods=['POST', 'GET'])
def files(path = ''):
    if not current_user.is_authenticated:
        flash('Kan ikke se filer, bruker er ikke logget inn', 'warning')
        return redirect(url_for('users.login'))
    
    if not con_is_active(current_user.ssh):
        logout_user()
        flash('Koblingen til filsystem har forsvunnet. Koble opp igjen', 'warning')
        return redirect(url_for('users.login'))

    #Split of parent directory and reconstruct path
    path_split = split('/' + path.strip('/'))
    if path_split[0] == '/':
        path_join = path_split[0] + path_split[1] 
    else:
        path_join = path_split[0] + '/' + path_split[1]
    
    #path_split = ('/Users/tir/Desktop/python/sas7bdat, testfil.sas7bdat')
    #path_join = '/Users/tir/Desktop/python/sas7bdat/testfil.sas7bdat'
    print(f'Path is: {path}, striped path is: {path_split}, joined path: {path_join}')
    
    #If root
    try:
        if path_split[1] == '':
            root = current_user.sftp.listdir_attr(path_split[0])
            current_user.lastdir = (path_split[0], root)
            return showDirectory(current_user.lastdir)
        else:
            parent = current_user.sftp.listdir_attr(path_split[0])
            entry = [entry for entry in parent if entry.filename == path_split[1]].pop()
            if S_ISDIR(entry.st_mode):
                listing = current_user.sftp.listdir_attr(path_join)
                current_user.lastdir = (path_join, listing)
                return showDirectory(current_user.lastdir)
            elif S_ISREG(entry.st_mode):
                #with tempfile.TemporaryFile(mode='w+b', 
                #            buffering=io.DEFAULT_BUFFER_SIZE) as tmp:
                    try:
                        file = current_user.sftp.file(path_join, 
                                mode='r', bufsize=io.DEFAULT_BUFFER_SIZE)
                        return showFile(path_join, path_split[1], file)
                    except IOError as ex:
                        flash(f'{path_join} could not be read, IOError {ex}', 'warning')
                        return showDirectory(current_user.lastdir)
            else:
                flash(f'{path_join} is neither evaluated to file or directory', 'warning')
                return showDirectory(current_user.lastdir)
    except FileNotFoundError as ex:
        flash(f'{path_join} is neither file or directory, FileNotFoundError {ex}', 'warning')
        return showDirectory(current_user.lastdir)        
    
def showDirectory(listing):
    parent, pathlist = listing
    parent = parent if parent != '/' else ''
    fo, fi = dict(), dict()
    for entry in pathlist:
        if S_ISDIR(entry.st_mode):
            #print(entry.filename + " is folder")
            fo[quote('/files' + parent + '/' + entry.filename)] = entry.filename
        elif S_ISREG(entry.st_mode):
            fi[quote('/files' + parent + '/' + entry.filename)] = entry.filename
            #print(entry.filename + " is file")
    return render_template('browser.html', folder=[fo], files=[fi])


def showFile(fullname, filename, file_object):
     
    try:
    #encoding='unicode_escape'
        df = pd.read_sas(file_object, format='sas7bdat', 
                         index=None, encoding=None, iterator=False,
                         chunksize = io.DEFAULT_BUFFER_SIZE)
        header = [col.name for col in df.columns]
        rows = df.read(2)
        row0 = rows.iloc[0].values.tolist()
        row1 = rows.iloc[1].values.tolist()
        
        split = os.path.splitext(fullname)
        jsonfile = {'gammelfil': fullname,
                    'nyfil' : split[0] + '_pseudo' + split[1],
                    'pseudo' : []
                    }
    except Exception as ex:
        return f'Pandas error: {ex}'
    if request.method == 'GET':
        return render_template('dropbox.html', orgfil=jsonfile['gammelfil'], nyfil=jsonfile['nyfil'],
                               header=header, row0=row0, row1=row1, 
                               jsonfile=jsonfile)
    elif request.method != 'POST':
        return 'Request method not GET or POST'
    
    #jsonfile['request'] = request.form.copy()
    
    jsonfile['pseudo'] = request.form.getlist('pseudo')
    #jsonfile['nyttfilnavn'] = request.form.get('nyttnavn')
    
    if request.form['submit_button'] == 'Oppdater konfigurasjonsfil':
        flash('Oppdater konfigurasjonsfil', 'info')
    elif request.form['submit_button'] == 'Pseudonymiser fil':
        flash('Pseudonymiserer fil', 'info')
        if not getattr(current_app, 'pseudoThread', None):
            current_app.pseudoThread = set()
        thread = threading.Thread(target=runPseudo, 
                                  args =(jsonfile['gammelfil'], 
                                         jsonfile['nyfil'],
                                         jsonfile['pseudo']
                                         ),
                                  name = 'pseudo' + str(len(set())))
        current_app.pseudoThread.add(thread)
        thread.start()
    else:
        return "Should not be reached"
    #varsx = sas_op.getVarnames(sas_op.getFilename(filename), sas_op.getPath(filename))
    #columns = varsx.iloc[:,0].to_list()
    return render_template('dropbox.html', orgfil=jsonfile['gammelfil'], nyfil=jsonfile['nyfil'],
                               header=header, row0=row0, row1=row1, 
                               jsonfile=jsonfile)

def runPseudo(orgfile, newfile, pseudo):
    pass

