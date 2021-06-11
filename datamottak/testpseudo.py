import unittest
import pandas as pd

from pyffx import FixedAlphabet

def getdataframe():
    df2 = pd.DataFrame({
'A': pd.Series([i+50 for i in range(5)], dtype='object'),
'B': pd.Series([f'j{i}ætest' for i in range(5)], dtype='object'),
'C': pd.Series(['6wæ6mgM', 'f4æLnmc', 'YgæfXjU', 'Mkæxmat', '6iæiPow'])
})
    return df2

class StringTests(unittest.TestCase):
    def testLoadDF(self):
        df2 = getdataframe()
        pseudo = FixedAlphabet(b'foo')
        
        var = 'B'
        df2[str('pseudo_' + var)] = df2.apply(
            lambda x: pseudo.encrypt(x[var]), axis=1)
        df2[str('pseudo_pseudo_'+ var)] = df2.apply(lambda x: pseudo.decrypt(x[str('pseudo_' + var)]), axis=1)
       