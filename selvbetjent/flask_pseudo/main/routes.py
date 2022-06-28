from flask import Blueprint
from flask import request, redirect, render_template, flash
from flask import url_for, current_app, g
from flask_login import current_user, logout_user
from stat import S_ISDIR, S_ISREG
from os.path import split 
import os
import io
from urllib.parse import quote
import pandas as pd


main = Blueprint('main', __name__)

#sas_op = SAS_Operasjoner()

@main.before_app_first_request
def init_main():
    if not hasattr(current_app, 'pseudoService'):
        raise AttributeError('no pseudoService set in main')
    current_app.pseudoService.start()

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
    
@main.route('/pseudo')
def pseudo():
    g.header = ('Gammelt filnavn', 'Nytt filnavn', 'Pseudo kolonner', 'Filtype')
    g.toDo = current_app.pseudoService.showList()
    g.errorHeader = ('Gammelt filnavn', 'Nytt filnavn', 'Pseudo kolonner', 'Error melding')
    g.error = current_app.pseudoService.error
    g.done = current_app.pseudoService.done
    g.tables = [('To Do list:', g.header, g.toDo),
                ('Done list:', g.header, g.done),
                ('Error list:', g.errorHeader, g.error)]
    return render_template('pseudo.html')
    
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
    #print(f'Path is: {path}, striped path is: {path_split}, joined path: {path_join}')
    
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
                    file = None
                    try:
                        file = current_user.sftp.file(path_join, 
                                mode='r', bufsize=io.DEFAULT_BUFFER_SIZE)
                        return showFile(path_join, path_split[1], file,
                                        current_app.pseudoService,
                                        current_user.sftp)
                    except IOError as ex:
                        flash(f'{path_join} could not be read, IOError {ex}', 'warning')
                        return showDirectory(current_user.lastdir)
                    finally:
                        if file:
                            file.close()
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


def showFile(fullname, filename, file_object, pseudoService, sftp):     
    rowNum = 2
    if hasattr(current_user, 'json_buffered'):
        if current_user.json_buffered[0]['gammelfil'] == fullname:
            g.json, g.header, g.rows = current_user.json_buffered
            
    if not hasattr(g, 'json'):
        try:
    #encoding='unicode_escape'
            df = pd.read_sas(file_object, format='sas7bdat', 
                         index=None, encoding=None, iterator=False,
                         chunksize = io.DEFAULT_BUFFER_SIZE)
            rows = df.read(rowNum)
            g.header = [col for col in df.column_names]
            g.rows = [rows.iloc[i].values.tolist() for i in range(rowNum)]
            split = os.path.splitext(fullname)
            g.json = {'gammelfil': fullname,
                    'nyfil' : split[0] + '_pseudo' + split[1],
                    'pseudoCol' : [],
                    'filetype' : 'sas'
                    }
            file_object.close()
            #print(f'json {g.json}')
        except Exception as ex:
            return f'Pandas error: {ex}'
    
    if request.method == 'GET':
        current_user.json_buffered = (g.json, g.header, g.rows)
        return render_template('dropbox.html')
    
    g.json['pseudoCol'] = [g.header[i] 
                           for i in range(len(g.header))
                           if request.form.get(f'pseudo{i}') == 'on']
    
    print(f'g.json:{g.json}')

    if request.form.get('submit_button') == 'Pseudonymiser fil':
        flash(f'Pseudonymiserer fil {g.json}', 'info')
        pseudoService.add(g.json['gammelfil'], g.json['nyfil'],
                          g.json['pseudoCol'], g.json['filetype'],
                          sftp)
        #return render_template('dropbox.html')
        del current_user.json_buffered
        return redirect(url_for('main.pseudo'))
    
    if request.form.get('submit_button') == 'Oppdater konfigurasjon':
        flash('Oppdater konfigurasjonsfil', 'info')
    
    if request.form.get('newFilename'):
        g.json['nyfil'] = request.form['newFilename']
        flash(f'Nytt filnavn:{g.json["nyfil"]}', 'info')
    
    current_user.json_buffered = (g.json, g.header, g.rows)
    return render_template('dropbox.html')
