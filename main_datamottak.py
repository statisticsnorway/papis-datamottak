# -*- coding: utf-8 -*-

import sys

sys.path.append('/ssb/stamme01/papis/_Programmer/python/')

import json
from io import StringIO
from pathlib import Path
import re
import os
import time


from datamottak import Pseudo
from datamottak import Funksjoner
from datamottak import loggFile
from datamottak import jsonHandler
from datamottak import Reader
from datamottak import SAS_Operasjoner


#Oppretter logg
try:
  logfile = sys.argv[2]
  logg = loggFile(logfile)
except IndexError:
  logg = loggFile()

loggen = logg.getLogger()

#Json-konfigurasjonsfil skal være input til programmet
try:
  json_input = sys.argv[1]
  loggen.info('Informasjon om json-fil:\n{}'.format(json_input))
except IndexError:
  loggen.exception('Input json-fil er ikke oppgitt') 
  sys.exit(1)

try:
  with open(json_input, 'r', encoding='utf-8-sig') as json_data_file:
    try:
      js_obj = json.loads(json_data_file.read())
    except ValueError as e:
      loggen.exception('Ingen gyldig json-fil:\n{}'.format(json_input))
      sys.exit(1)

except FileNotFoundError:
  loggen.exception('Ingen slik fil:\n{}'.format(json_input))
  sys.exit(1)



# Henter ut nødvendige dictionaries fra json-spesifikasjon
jsH = jsonHandler(js_obj, loggen)
fileObject = jsH.getFileObject() 
filename = jsH.getPath(fileObject) + jsH.getFilename(fileObject)
funcObject = jsH.getFuncObject()


# Henter ut alle aktuelle funksoner fra biblioteket
functions_list = list(set(dir(Funksjoner()) + dir(Pseudo())))
#loggen.info('Informasjon om funksjoner:\n{}'.format(functions_list))


###
# Skal legge til info om format på sas-fil her
###
sas_op = SAS_Operasjoner()
format_dict = sas_op.getFormatDict(sas_op.getFilename(filename), sas_op.getPath(filename))


start_time = time.time()

# Innlesing av fil
reader = Reader()
file_names_dict = reader.getFileNameWithLowerCase(filename) #Skal ikke være case-sensitiv

fileExtension = reader.getExtension(filename, loggen)
loggen.info('Fileextension: {0}'.format(fileExtension))  
if fileExtension in ('.SAS7BDAT', '.sas7bdat'):
  #df = reader.read_sas(file_names_dict[os.path.basename(filename).lower()], loggen)
  df = sas_op.SASTodf(file_names_dict[os.path.basename(filename).lower()]) 
elif fileExtension == '.csv':
  df = reader.read_csv(fileObject, file_names_dict[os.path.basename(filename).lower()], loggen)

print("--- %s seconds ---" % (time.time() - start_time))

loggen.info('Informasjon om filnavn:\n{}'.format(file_names_dict))

# Standard output er til skjerm. Endrer dette for å få utskrift til logg.
buf = StringIO()
df.info(buf=buf)

column_names_dict = {x.lower(): x for x in df.columns.tolist()}

loggen.info('Informasjon om innlest fil:\n{}'.format(buf.getvalue()))
loggen.info('Kolonnenavn:\n{}'.format(column_names_dict.keys()))
loggen.info('FuncObject:\n{}'.format(funcObject))


##################################################
#                                                #
# Utfører spesifikajsoner (pseudonymisering etc) #
#                                                #
##################################################
performPseudo_variables = []
to_be_deleted_vars = []
rename_variables = {}
RENAME_COLUMN = 'pseudo_'
if jsH.validFuncNameAndColumnName(funcObject, functions_list, column_names_dict, loggen):
  for f in funcObject:
    kolonne = f.get('fraKolonne').lower()
    if f.get('funksjonsNavn') == 'performPseudo':
      performPseudo_variables.append(column_names_dict[kolonne])
      rename_variables[column_names_dict[kolonne]] = str(RENAME_COLUMN + column_names_dict[kolonne])
      if bool(format_dict):
        del format_dict[column_names_dict[kolonne]]
    if f.get('funksjonsNavn') != 'performPseudo':
      if f.get('funksjonsNavn') == 'del_column':
        to_be_deleted_vars.append(column_names_dict[kolonne]) 
        del format_dict[column_names_dict[kolonne]]
      else:
        kolonne = f.get('fraKolonne').lower()
        funksjon = getattr(Funksjoner(), f.get('funksjonsNavn'))
        df[f.get('nyKolonne')] = df[column_names_dict[kolonne]].apply( lambda x : funksjon(x) )

  if performPseudo_variables:
    pseudo = Pseudo()
    pseudo.performPseudo(df, performPseudo_variables)
  if rename_variables:
    df.rename(rename_variables, axis = 1, inplace=True)
  if to_be_deleted_vars:
    df.drop(to_be_deleted_vars, axis = 1)

#####################
#                   #
# Oppretter csv-fil #
#                   #
#####################

new_filename = jsH.getPath(fileObject) +'pseudo_' + Path(jsH.getFilename(fileObject)).stem # + '.csv'
filename = new_filename.replace("3_Kontrollert","5_Klart")
loggen.info('Ny fil:\n{}'.format(filename))

df.to_csv(filename+'.csv', sep=';',index=False)


##################################
# Skriver info om fil til loggen #
##################################
buf2 = StringIO()
df.info(buf=buf2)

loggen.info('Informasjon om ferdig behandlet fil:\n{}'.format(buf2.getvalue()))

loggen.info("Variable som er blitt pseudonymisert:\n{}".format(performPseudo_variables))
loggen.info("Variable som er fjernet fra innfila:\n{}".format(performPseudo_variables+to_be_deleted_vars))

if 'gyldig_id' in df.columns:
  loggen.info("Gyldig id-kontroll:\n{}".format(df['gyldig_id'].value_counts()))


##################################
# Lager sas.fil                  #
##################################
#sas_sti = jsH.getPath(fileObject).replace("3_Kontrollert", "5_Klart")
test_sti = '/ssb/stamme01/papis/_Programmer/python'
sas_op.dfToSAS(df, test_sti, 'pseudo_' + Path(jsH.getFilename(fileObject)).stem, format_dict)
loggen.info('SAS-fil opprettet')

#print(format_dict)
loggen.info('Filnavn:\npseudo_{}'.format(Path(jsH.getFilename(fileObject)).stem))

############################################################
# Rename loggfil                                           #
# Logg ligger i Oppstartskatalog                           #
# Flyttes til logg-katalog for den spesifikke statistikken #
############################################################
regex = re.compile(r'\D+(\d+).json')
nr = regex.findall(json_input)

new_logname = logg.getLogname()
if nr:
   new_logname = logg.getLogname().replace("pseudo", nr[0]+"_"+"pseudo")  

stamme_innfil = jsH.getPath(fileObject)
mellom_fil = new_logname.replace("/ssb/stamme01/papis/Oppstart/",stamme_innfil)
logfile = mellom_fil.replace("3_Kontrollert","6_Logger_rapporter")

os.rename(logg.getLogname(), logfile)


