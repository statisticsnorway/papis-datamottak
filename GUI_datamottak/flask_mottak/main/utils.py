import pandas as pd
import json
from flask import flash



def read_sas_file(fileName, encoding='unicode_escape'):
  df = pd.read_sas(fileName, format='sas7bdat', index=None, encoding=encoding, iterator=False)
  return df.head(2)

#read file
def getConfigmal(data):
  with open('config_sas.json', 'r') as myfile:
    data=json.loads(myfile.read())
    return data


def update_json(sas_op, filename, data, pseudo_liste='', delete_liste='', katalog=''):
  fil = data['fil']
  fil['sti'] = sas_op.getPath(filename) + '/'
  fil['navn'] = sas_op.getFilename(filename) + '.sas7bdat'

  if katalog != '':
    fil['utkatalog'] = katalog

  for var in pseudo_liste:
    ny = {"funksjonsNavn": "performPseudo",
          "fraKolonne": var,
          "nyKolonne": "pseudo_" + var}
    funksjon = data['funksjon'].append(ny)

  for var in delete_liste:
    ny = {"funksjonsNavn": "del_column",
          "fraKolonne": var
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

def variabel_verdi_dict(df, loggfil):
    if df is None:
        flash(f'{loggfil} har ingen records! Antakelig innebærer dette at sas-fil fra fnr-leting er tom.',
              'warning')
        return None
    if not df.empty:
        df.loc[df['verdi'].str.strip() == '.', 'verdi'] = None
        df.loc[df['verdi'].str.strip() == '', 'verdi'] = None
        df['verdi'] = df['verdi'].str.strip()
        variabler = df['variabel'].tolist()
        verdi = df['verdi'].tolist()
        var_verdi = dict(zip(variabler, verdi))

    return var_verdi

def get_pseudo_vars(vars, fnr):
    # Under fnr-leting/kontroll fjernes fnr-variabel.
    # Ersattes av tre nye variable: fnr_orig, fnr_naa, snr
    nye = ['fnr_orig', 'fnr_naa', 'snr']
    pseudo_vars = vars + nye
    pseudo_vars.append(fnr)
    pseudo_vars = set(pseudo_vars)

    try:
        pseudo_vars.remove(fnr)
    except ValueError:
        flash(f'Prøver å fjerne verdi fra liste som ikke finnes i listen fra før - {fodselsnr}!',
                  'warning')

    return pseudo_vars