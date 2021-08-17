import sys
sys.path.append('/ssb/stamme01/papis/_Programmer/PYTHON/saspy-main')
from saspy import SASsession


sas = SASsession()


def lag_sasfil(df, sti, filnavn):
  sas.saslib('MyLib', path=sti)
  sas.dataframe2sasdata(df, filnavn, libref='MyLib')

