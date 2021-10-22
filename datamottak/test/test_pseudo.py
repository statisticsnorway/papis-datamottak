from ..pseudo import Pseudo
import unittest
import pandas as pd
from papis_service.http_server import SimpleHttpServer
from pandas.testing import assert_frame_equal

class TestPseudo(unittest.TestCase, SimpleHttpServer):
    data = {
        "col1" : ['23er', '', '.r'],
        "col2" : ['asdf', 'øøøø', '123']
        }
    pseudo = {
        "col1" : ['2YZF', '', '.k'],
        "col2" : ['ZVay', 'øøøø', 'h61']
        }
    def testPseudo(self):
        p = Pseudo()
        df = pd.DataFrame(self.data)
        p.performPseudo(df, ["col1","col2"])
        assert_frame_equal(df, pd.DataFrame(self.pseudo))
    
    def testPseudoStr(self):
        p = Pseudo()
        df = pd.DataFrame(self.data)
        p.performPseudo(df, "col1")
        p.performPseudo(df, "col2")
        assert_frame_equal(df, pd.DataFrame(self.pseudo))        
        
    def testPseudoSingleMessage(self):
        p = Pseudo()
        df = pd.DataFrame(self.data)
        p.performPseudoSingleMessage(df, ["col1","col2"])
        assert_frame_equal(df, pd.DataFrame(self.pseudo))      
    