# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 14:34:56 2021

@author: oeh
"""

from papis_service.http_server import SimpleHttpServer
from papis_service.client import ClientUrl


class Pseudo:

  def __init__(self, mode = 'test/'):
    self.mode = mode
    
  def close(self):
      SimpleHttpServer.tearDownClass()
    
  def performPseudo(self, df, varlist):
    if not getattr(SimpleHttpServer, "TCPServer", None):
        SimpleHttpServer.setUpClass()
    pseudo = ClientUrl(SimpleHttpServer.address, self.mode)
    if not isinstance(varlist, list):
        varlist = [varlist]
    for var in varlist:
      col_list = df[var].tolist()
      p_dict = pseudo.jsonencryptD(col_list)
      df[var].replace(p_dict, inplace=True)

  def performPseudoSingleMessage(self, df, varlist):  
    if not getattr(SimpleHttpServer, "TCPServer", None):
        SimpleHttpServer.setUpClass()
    pseudo = ClientUrl(SimpleHttpServer.address, self.mode)
    if not isinstance(varlist, list):
        varlist = [varlist]
    for var in varlist:
      df[var] = df.apply(
            lambda x: pseudo.encrypt(x[var]), axis=1)
      
  def performSasPseudo(self, filename, varlist):
     raise NotImplementedError()

