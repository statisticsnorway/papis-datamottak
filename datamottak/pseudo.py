# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 14:34:56 2021

@author: oeh
"""

from papis_service.common.configureServerEnv import ConfigureServerEnv
from .sas.pseudosas7bdat import PseudoSas7bdat

class Pseudo:
  _similar = {"AUTH" : "NONE", "AUTH_LOCATION" : None,
        "OPERATION" : "BOTH", "KEY_SOURCE" : "KEY_LOCATION",
        "KEY_TYPE" : "BYTES", "CACHE_LOCATION" : None
#        ,"CACHE_SOURCE" : "NONE", "CACHE_PARAM" : None
    }

  _test3 = {'CACHE_SOURCE' : "SQL" , "CACHE_PARAM" : 100000,
             "PSEUDO_ALGORITHM" : "FF3", "KEY_LOCATION" : 
             'EF4359D8D580AA4F7F036D6F04FC6A94',
             "KEY_TYPE" : "FROMHEX", "CACHE_LOCATION" : None}

  _cacheTypes = { 
                   "test3": dict(tuple(_similar.items())+tuple(_test3.items()))
    }
  
  _configDict = { "BROWSER" : _cacheTypes.copy(),
           "API": _cacheTypes.copy(),
           "SSL" : False, "ALLOW_GET" : True,
           "DATABASE" : ":memory:",
           "HOST" : "localhost", "PORT" : 0}
  
  def __init__(self, config = _configDict, interface= 'api', environ = 'test3'):
    config = ConfigureServerEnv.configure(config)
    if interface == 'api':
        env = config.apiEnv.get(environ)
    elif interface == 'browser':
        env = config.browserEnv.get(environ)
    else:
        raise AttributeError('inteface not api or config')
        
    if not env:
        raise AttributeError(f'Pseudo mode: {environ} not supported. Supported {list(config.apiEnv.keys())}')
    else:
        self.cache = env.cache
    
  def close(self):
      pass
    
  def performPseudo(self, df, varlist, encrypt = True):
    col_set = set()
    for var in varlist:
        col_set.update(df[var].tolist())
    if encrypt:
        p_dict = self.cache.encryptSet(col_set)
    else:
        p_dict = self.cache.decryptSet(col_set)
    for var in varlist:
        df[var].replace(p_dict, inplace=True)
  
  #Returns a temporary file
  def performPseudoSasTemp(self, filename, varlist, encrypt = True, tempDir=None):
    file = PseudoSas7bdat(filename)
    temp = file.pseudo(varlist)
    file.close()
    return temp
          
#  def performPseudoSingleMessage(self, df, varlist):  
#    if not getattr(SimpleHttpServer, "TCPServer", None):
#        SimpleHttpServer.setUpClass()
#    pseudo = ClientUrl(SimpleHttpServer.address, self.mode)
#    if not isinstance(varlist, list):
#        varlist = [varlist]
#    for var in varlist:
#      df[var] = df.apply(
#           lambda x: pseudo.encrypt(x[var]), axis=1)
      


