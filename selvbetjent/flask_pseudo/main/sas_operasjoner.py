import sys
import pathlib
import pandas as pd

sys.path.append('/ssb/stamme01/papis/_Programmer/python/saspy_main')
from saspy import SASsession

class SAS_Operasjoner:
    date_format_list = ['DATE', 'DAY', 'DDMMYY', 'DOWNAME', 'EURDF', 'HHMM', 'JULDAY', 'JULIAN', 'MINGUO', 'MMDDYY',
                        'MMSS', 'MMYY', 'MON',
                        'WEEK', 'NENGO', 'PDJUL', 'YYMON', 'QTR', 'DTWKDAT', 'YEAR', 'DTYYQC', 'HOUR', 'TIME', 'TOD',
                        'YYMMDD', 'YYQ']

    def __init__(self):
        self.sas = SASsession()

    def dfToSAS(self, df, sti, filnavn, outfmts={}):
        outfmts = {k: v for k, v in dict(outfmts).items() if v == v}
        self.datetimes = self.getDateFormats(outfmts, df)
        self.sas.saslib('MyLib', path=sti)
        self.sas.dataframe2sasdata(df, filnavn, libref='MyLib', datetimes=self.datetimes, outfmts=outfmts)

    def getFormatDict(self, sasfil, sti):
        self.sas.saslib('Content', path=sti)
        hr = self.sas.sasdata(table=sasfil, libref='Content')
        if 'Format' in hr.columnInfo().columns:
            hr_df = hr.columnInfo()[['Variable', 'Format']]
            format_dict = dict(zip(hr_df.Variable, hr_df.Format))

            return format_dict

        return {}

    def getDateFormats(self, format_dict, df):
        self.datetime_dict = {}
        if bool(format_dict):
            for self.k, self.v in format_dict.items():
                if self.v == self.v:
                    res = [self.d for self.d in self.date_format_list if (self.d.lower() in self.v.lower())]
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
