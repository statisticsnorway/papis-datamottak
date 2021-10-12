import sys
import pathlib
from io import StringIO
import pandas as pd

'''
'''
sys.path.append('/ssb/stamme01/papis/_Programmer/python/saspy_main')
from saspy import SASsession

#sas = SASsession()


class SAS_Operasjoner:
  #sas = SASsession()

  date_format_list = ['DATE', 'DAY', 'DDMMYY', 'DOWNAME', 'EURDF', 'HHMM', 'JULDAY', 'JULIAN', 'MINGUO', 'MMDDYY', 'MMSS', 'MMYY', 'MON', 
                      'WEEK', 'NENGO', 'PDJUL', 'YYMON', 'QTR', 'DTWKDAT', 'YEAR', 'DTYYQC', 'HOUR', 'TIME', 'TOD', 'YYMMDD', 'YYQ']
  
  def __init__(self):
    self.sas = SASsession()

  def dfToSAS(self, df, sti, filnavn, outfmts = {}):
    outfmts =  {k:v for k,v in dict(outfmts).items() if v == v}
    self.datetimes = self.getDateFormats(outfmts, df)
    #print(self.datetimes) 
    #print(outfmts) 
    self.sas.saslib('MyLib', path=sti)
    self.sas.dataframe2sasdata(df, filnavn, libref='MyLib', datetimes=self.datetimes, outfmts=outfmts)

  def getFormatDict(self, sasfil, sti):
    self.sas.saslib('Content', path=sti)
    hr = self.sas.sasdata(table=sasfil, libref='Content')
    #print(hr.columnInfo())
    if 'Format' in hr.columnInfo().columns:
      hr_df = hr.columnInfo()[['Variable','Format']]
      #format_dict = hr_df.values #Her m jeg ha endret p koden for denne virker ikke som nskelig lenger
      format_dict = dict(zip(hr_df.Variable, hr_df.Format))
     
      return format_dict

    return {} 

  def getDateFormats(self, format_dict, df):
    self.datetime_dict = {}
    if bool(format_dict):
      for self.k, self.v in format_dict.items():
        if self.v == self.v:
          res = [self.d for self.d in self.date_format_list if ( self.d.lower() in self.v.lower() )]
          if bool(res):
            self.datetime_dict[self.k] = 'date'
            df[self.k] = pd.to_datetime(df[self.k])  
          
      return self.datetime_dict

    return self.datetime_dict


  def SASTodf(self, filnavn):
    self.sti = str(pathlib.Path(filnavn).parent)
    self.filn = pathlib.Path(filnavn).stem
    self.sas.saslib('saslib', path=self.sti)
    self.df = self.sas.sasdata2dataframe(self.filn, libref='saslib', method='CSV')
    return self.df

  def getPath(self, filename):
    self.path = str(pathlib.Path(filename).parent)
    return self.path

  def getFilename(self, filename):
    self.fileName = pathlib.Path(filename).stem
    return self.fileName
   


#sasGo = SAS_Operasjoner()


#df = sasGo.SASTodf('/ssb/stamme03/funkhem/analyse/wk24/papistest/ortok_innlest')
#print(type(df))
#sasGo.dfToSAS(df, '/ssb/stamme01/papis/_Programmer/python/papis-datamottak/datamottak', 'funkhem2', formater)

#df1 = sasGo.content('funkhem', '/ssb/stamme01/papis/_Programmer/python/papis-datamottak/datamottak')
#df2 = sasGo.content('funkhem2', '/ssb/stamme01/papis/_Programmer/python/papis-datamottak/datamottak')


#sasGo.SASTodf('/ssb/stamme01/papis/_Programmer/python/papis-datamottak/datamottak/funkhem')
#sasGo.content('pseudo_ortok_innlest', '/ssb/stamme03/funkhem/analyse/wk24/papistest')
#sasGo.SASTodf('/ssb/stamme03/funkhem/analyse/wk24/papistest/pseudo_ortok_innlest')

#print(sasGo.getPath('/ssb/stamme03/funkhem/analyse/wk24/papistest/pseudo_ortok_innlest'))
#print(sasGo.getFilename('/ssb/stamme03/funkhem/analyse/wk24/papistest/pseudo_ortok_innlest.sas7bdat'))

#formater = sasGo.getFormatDict('ortok_innlest', '/ssb/stamme03/funkhem/analyse/wk24/papistest')
#formater2 = sasGo.getFormatDict('pseudo_ortok_innlest', '/ssb/stamme01/papis/_Programmer/python')
#fd = sasGo.getFormatDict('feng', '/ssb/stamme01/papis/_Programmer/python/')

#formater = sasGo.getFormatDict('ufdinye_201606', '/ssb/stamme01/papis/F-G-H-I-J/Funkhem/3_Kontrollert')
#formater2 = sasGo.getFormatDict('pseudo_ufdinye_201606', '/ssb/stamme01/papis/F-G-H-I-J/Funkhem/5_Klart')

#print(formater)
#print(formater2)

