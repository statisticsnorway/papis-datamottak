# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 08:28:15 2021

@author: oeh
"""

import sys
import pandas as pd
import json
from PAPIS_exceptions import FuncInvalidConfigError, FuncError, FileInvalidConfigError, ArgvInvalidConfigError
from PAPIS import id_sjekk, kjonn, fodselsdato
import PAPIS
import PAPIS_pseudo
from PAPIS_pseudo import performPseudo, del_column
from PAPIS_readers import reader
import logging
from datetime import datetime
from io import StringIO
from pathlib import Path
import glob, os



logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

timestamp = datetime.now().strftime('pseudo_%H_%M_%S_%d_%m_%Y.log')

LOG_FILENAME = r"/ssb/stamme01/papis/K-L-M-N-O/Nasjonale_prover/6_Logger_rapporter/"+timestamp

file_handler = logging.FileHandler(LOG_FILENAME)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

functions_list = list(set(dir(PAPIS) + dir(PAPIS_pseudo)))#[o for o in dir(PAPIS)]


try:
  json_input = sys.argv[1]
  logger.info('Informasjon om json-fil:\n{}'.format(json_input))
except IndexError:
  logger.exception('Input json-fil er ikke oppgitt') 
  sys.exit(1)
  
try:
  with open(json_input, 'r', encoding='utf-8-sig') as json_data_file:
    try:
      js_obj = json.loads(json_data_file.read())
    except ValueError as e:
      logger.exception('Ingen gyldig json-fil:{}'.format(json_input))
      sys.exit(1)
	    
except FileNotFoundError:
  logger.exception('Ingen slik fil:{}'.format(json_input))
  sys.exit(1)
	
def getFileObject(jsonObj):
  file = jsonObj.get('fil')
  if file is None:
    logger.error('Mangler informasjon om filinnhold')
    raise FileInvalidConfigError("Mangler informasjon om fil")

  return file


file = getFileObject(js_obj)


def getPath(fileDict):
  path = fileDict.get('sti')
  if path is None:
    logger.error('Filsti ikke definert')
    raise FileInvalidConfigError('Filsti ikke definert')
  return path

def getFilename(fileDict):
  name = fileDict.get('navn')
  if name is None:
    logger.error('Filnavn ikke definert')
    raise FileInvalidConfigError('Filnavn ikke definert')

  return name


filename = getPath(file) + getFilename(file)

#Legger filnavn i dictionary. Ønsker at oppgitt filnavn ikke trenger å være case-sensitiv
#file_names_dict = {}
#def glob_files(files):
#  for f in glob.glob(files):
#    file_names_dict[os.path.basename(f).lower()] = os.path.basename(f)

#glob_files(os.path.dirname(filename)+'//*.csv')
#glob_files(os.path.dirname(filename)+'//*.sas7bdat')

df = reader(file, filename, logger) 
#file_names_dict[os.path.basename(filename).lower()], logger)

column_names_list = [x.lower() for x in df.columns.tolist()]
column_names_dict = {x.lower(): x for x in df.columns.tolist()}


#info er default til terminal. Endrer det her
buf = StringIO()
df.info(buf=buf)

logger.info('Informasjon om innlest fil:\n{}'.format(buf.getvalue()))
logger.info('Kolonnenavn:\n{}'.format(column_names_list))


def getFuncObject(jsonObj):
  function = jsonObj.get('funksjon')
  if function is None:
    logger.error('Mangler informasjon om funksjoner som skal brukes')
    raise FuncInvalidConfigError("Mangler informasjon om funksjoner som skal brukes")

  return function

        
function = getFuncObject(js_obj)


def validFuncNameAndColumnName(funcDict):
  for f in funcDict:
    func_name = f.get('funksjonsNavn')
    if func_name is None:
      logger.error('Funksjonsnavn mangler')
      raise FuncInvalidConfigError("Funksjonsnavn mangler")
    if func_name in functions_list:
      pass
    else:
      logger.error("Ukjent funksjonsnavn : {0}".format(func_name))
      raise FuncError("Ukjent funksjonsnavn : {0}".format(func_name))
           
    column_name = f.get('fraKolonne')
    if column_name is None:
      logger.error("Kolonne som skal behandles er ikke definert")
      raise FuncInvalidConfigError("Kolonne som skal behandles er ikke definert")
    if column_name.lower() not in column_names_list:
      logger.error("Ukjent kolonnenavn : {0}".format(column_name))
      raise FuncError("Ukjent kolonnenavn : {0}".format(column_name))
            
    new_column_name = f.get('nyKolonne')
    if new_column_name is None:
      if f.get('funksjonsNavn') == 'del_column':
        pass
      else: 
        logger.error("Nytt kolonnenavn er ikke definert")
        raise FuncInvalidConfigError("Nytt kolonnenavn er ikke definert")
            
    return True


performPseudo_variables = []
to_be_deleted_vars = []
if validFuncNameAndColumnName(function):
  for f in function:
    kolonne = f.get('fraKolonne').lower()
    if f.get('funksjonsNavn') == 'performPseudo':
      performPseudo_variables.append(column_names_dict[kolonne])
    if f.get('funksjonsNavn') != 'performPseudo':
      if f.get('funksjonsNavn') == 'del_column':
        to_be_deleted_vars.append(column_names_dict[kolonne])
      else:
        kolonne = f.get('fraKolonne').lower()
        df[f.get('nyKolonne')] = df[column_names_dict[kolonne]].apply(eval(f.get('funksjonsNavn')))	    

  if len(performPseudo_variables) > 0:
    performPseudo(df, performPseudo_variables)
    #del_column(df, performPseudo_variables+to_be_deleted_vars)

new_filename = getPath(file) +'pseudo_' + Path(getFilename(file)).stem + '.csv'
logger.info('Ny fil:\n{}'.format(new_filename))

df.to_csv(new_filename, sep=';',index=False)
#print(df['gyldig_id'].value_counts())
buf2 = StringIO()
df.info(buf=buf2)

logger.info('Informasjon om ferdig behandlet fil:\n{}'.format(buf2.getvalue()))

logger.info("Variable som er blitt pseudonymisert:\n{}".format(performPseudo_variables))
logger.info("Variable som er fjernet fra innfila:\n{}".format(performPseudo_variables+to_be_deleted_vars))
logger.info("Gyldig id-kontroll:\n{}".format(df['gyldig_id'].value_counts()))








