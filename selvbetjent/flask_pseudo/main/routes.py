import os
from pathlib import Path

from flask import Blueprint
from flask import request, redirect, render_template, json, flash, url_for
from flask_pseudo.main.utils import *
from flask_pseudo.main.sas_operasjoner import *
from flask_pseudo.models import Log
from flask_login import current_user

from flask_pseudo import db


main = Blueprint('main', __name__)

with open('config_mal.json', 'r') as myfile:
  data=json.loads(myfile.read())

sas_op = SAS_Operasjoner()

 

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
      path = request.form['folder']
      return redirect(url_for('main.about', path=path))
    else:
      flash('Oppgi stammekatalog</fil>', 'warning')



@main.route('/files/')
@main.route('/files/<path:path>', methods=['POST', 'GET'])
def about(path=''):
    root = '/ssb/'

    file = getPath(path) if path != '' else normpath(join(root,path))

    if not (Path(root) in Path(file).parents 
            or Path(root) == Path(file)):
        flash(f'{file} is not below {root}', 'warning')
    if not (isfile(file) or isdir(file)):
        flash(f'{file} is neither file or directory', 'warning')
        
    
    st = []
    fi = []
    if isdir(file):
      update_json(sas_op,file,data)
      if os.access(file, os.R_OK):
        flash(f'You are searching directory {file}', 'info')
        traverse = next(os.walk(file))
        if path != '':
          dic=dict([(f'{path}/..', '..')])
          st.append(dic)

        for dirs in traverse[1]:
          d = join(path, dirs)
          dic=dict([(d, dirs)])
          st.append(dic)

        for files in traverse[2]:
          if allowed_file(files):
            d = join(path, files)
            dic=dict([(d, files)])
            fi.append(dic)
      else:
        flash(f'Ikke tilgang til {file}', 'warning')

    elif isfile(file): 
      if os.access(file, os.R_OK):
        flash(f'File {file}', 'info')
        p_row = ''
        pseudofil = ''
        p_header = ''
        df = read_file(file)
        header = df.columns.tolist()
        row = df.iloc[0].values.tolist()
        katalog=''

        if request.method == 'POST':
          if request.form['submit_button'] == 'Oppdater konfigurasjonsfil':
            pseudo_vars = request.form.getlist('pseudo')
            delete_vars = request.form.getlist('delete')
            update_json(sas_op, file, data, pseudo_vars, delete_vars, '')

          elif request.form['submit_button'] == 'katalog':
            root = '/ssb/'
            path = request.form['folder']
            katalog = getPath(path) if path != '' else normpath(join(root,path))
            if katalog != '/ssb':
              if os.access(katalog, os.R_OK):
                update_json(sas_op, file, data, '', '', katalog)
              else:  
                flash(f'{katalog} is not valid', 'warning')
            else:
              flash('Oppgi stammekatalog</fil>', 'warning')
          
          elif request.form['submit_button'] == 'Pseudonymiser fil':
            configfil = sas_op.getPath(file)+'/config.json'
            if config_ready(data):
              with open(configfil, 'w') as f:
                json.dump(data, f, indent=4)
              os.system('python3 /ssb/stamme01/papis/_Programmer/python/papis-datamottak/main_datamottak.py '+ configfil) 
              
              fil = data['fil']
              pseudo=[]
              deleted = []
              katalog = fil['utkatalog']
              for f in data['funksjon']:
                if f['funksjonsNavn'] == 'performPseudo':
                  pseudo.append(f['fraKolonne'])
                if f['funksjonsNavn'] == 'del_column':
                  deleted.append(f['fraKolonne'])
              
              log = Log(kildefil=fil['sti']+fil['navn'], pseudo_var=", ".join(pseudo), delete_var=", ".join(deleted), resultatfil=katalog+'/'+'pseudo_'+sas_op.getFilename(file)+'.sas7bdat', user_id=current_user.id)
              db.session.add(log)
              db.session.commit()
              flash('Pseudomymisert fil laget. Se logger', 'success')            
            else:
              flash('Oppdater konfigurasjonsfil', 'warning')

          elif request.form['submit_button'] == 'Vis pseudofil':
            #fil = data['fil']
            #katalog = fil['utkatalog']
            if len(katalog) > 1:
              filename = katalog +'/'+'pseudo_'+sas_op.getFilename(file)+'.sas7bdat'
            else:
              filename = sas_op.getPath(file)+'/'+'pseudo_'+sas_op.getFilename(file)+'.sas7bdat'
            if isfile(filename):
              if len(katalog) > 1:
                pseudo_df = read_file(katalog +'/'+'pseudo_'+sas_op.getFilename(file)+'.sas7bdat')
              else:
                pseudo_df = read_file(sas_op.getPath(file)+'/'+'pseudo_'+sas_op.getFilename(file)+'.sas7bdat')
		
              p_header = pseudo_df.columns.tolist()
              p_row = pseudo_df.iloc[0].values.tolist()
              
            else:
              flash('Pseudonymisert fil er ikke laget.', 'warning')

          else:
            pass


        vars = sas_op.getVarnames(sas_op.getFilename(file), sas_op.getPath(file))
        columns = vars.iloc[:, 0].to_list()
        return render_template('dropbox.html', fil=file, header=header, row=row, p_header=p_header, p_row=p_row, varnames=columns, jsonfile=json.dumps(data, indent=4), pseudofil=pseudofil)

      else:
        flash(f'Ikke tilgang til {file}', 'warning')

    return render_template('browser.html', folder=st, files=fi)

