import sys
from os.path import normpath, join, isdir, isfile
from flask import current_app
import pandas as pd
import json


sys.path.append('/ssb/stamme01/papis/_Programmer/python/papis-datamottak/datamottak')
#from sas_operasjoner import *


#read file
def getConfigmal(data):
  with open('config_mal.json', 'r') as myfile:
    data=json.loads(myfile.read())
    return data


def read_file(fileName, encoding='unicode_escape'):
  df = pd.read_sas(fileName, format='sas7bdat', index=None, encoding=encoding, iterator=False)
  return df.head(2)

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['EXTENSIONS']

def update_json(sas_op, filename, data, pseudo_liste='', delete_liste = '',  katalog=''):
  fil = data['fil']
  fil['sti'] = sas_op.getPath(filename)+'/'
  fil['navn'] = sas_op.getFilename(filename)+'.sas7bdat'
  
  if katalog != '':
    fil['utkatalog'] = katalog
 
  for var in pseudo_liste:
    ny = {"funksjonsNavn": "performPseudo",
          "fraKolonne" : var,
          "nyKolonne" : "pseudo_"+var}
    funksjon = data['funksjon'].append(ny)
  
  for var in delete_liste:
    ny = {"funksjonsNavn": "del_column",
          "fraKolonne" : var
         }
    funksjon = data['funksjon'].append(ny)

  if len(pseudo_liste) < 1 and katalog == '':
    fil['sti'] = ''
    fil['navn'] = ''
    data['funksjon'].clear()
    fil['utkatalog'] = ''
    
 
def config_ready(data):
  fil = data['fil']
  if len(data['funksjon']) < 1:
    return False
  elif len(fil['sti']) < 1 or len(fil['navn']) < 1: 
    return False
  else:
    return True

def getPath(path):
  normpath1 = normpath(join('/ssb/stamme01',path))
  normpath2 = normpath(join('/ssb/stamme02',path))
  normpath3 = normpath(join('/ssb/stamme03',path))
  normpath4 = normpath(join('/ssb/stamme04',path))
  normpath5 = normpath(join('/ssb/',path))
  normpath6 = normpath(join('/ssb/bruker/',path))

  if isfile(normpath1) or isdir(normpath1):
    return normpath1
  elif isfile(normpath2) or isdir(normpath2):
    return normpath2
  elif isfile(normpath3) or isdir(normpath3):
    return normpath3
  elif isfile(normpath4) or isdir(normpath4):
    return normpath4
  elif isfile(normpath5) or isdir(normpath5):
    return normpath5
  elif isfile(normpath6) or isdir(normpath6):
    return normpath6
  else:
    return path
