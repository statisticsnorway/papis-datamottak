# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 08:28:15 2021

@author: oeh
"""

from datamottak.exceptions import * #FuncInvalidConfigError, FuncError, FileInvalidConfigError, ArgvInvalidConfigError

class jsonHandler:
  def __init__(self, jsonObj, logger):
    self.jsonObj = jsonObj
    self.logger = logger
	
  def getFileObject(self):
    self.file = self.jsonObj.get('fil')
    if self.file is None:
      self.logger.error('Mangler informasjon om filinnhold')
      raise FileInvalidConfigError("Mangler informasjon om fil")

    return self.file


  def getPath(self, jsonFileObj):
    self.path = jsonFileObj.get('sti')
    if self.path is None:
      self.logger.error('Filsti ikke definert')
      raise FileInvalidConfigError('Filsti ikke definert')
    return self.path

  def getFilename(self, jsonFileObj):
    self.name = jsonFileObj.get('navn')
    if self.name is None:
      self.logger.error('Filnavn ikke definert')
      raise FileInvalidConfigError('Filnavn ikke definert')

    return self.name


  def getFuncObject(self):
    self.function = self.jsonObj.get('funksjon')
    if self.function is None:
      self.logger.error('Mangler informasjon om funksjoner som skal brukes')
      raise FuncInvalidConfigError("Mangler informasjon om funksjoner som skal brukes")

    return self.function

        
  def validFuncNameAndColumnName(self, funcDict, functions_list, column_names_dict, logger):
    for self.f in funcDict:
      self.func_name = self.f.get('funksjonsNavn')
      if self.func_name is None:
        logger.error('Funksjonsnavn mangler')
        raise FuncInvalidConfigError("Funksjonsnavn mangler")
      if self.func_name in functions_list:
        pass
      else:
        logger.error("Ukjent funksjonsnavn : {0}".format(self.func_name))
        raise FuncError("Ukjent funksjonsnavn : {0}".format(self.func_name))
           
      self.column_name = self.f.get('fraKolonne')
      if self.column_name is None:
        logger.error("Kolonne som skal behandles er ikke definert")
        raise FuncInvalidConfigError("Kolonne som skal behandles er ikke definert")
      if self.column_name.lower() not in column_names_dict.keys():
        logger.error("Ukjent kolonnenavn : {0}".format(self.column_name))
        raise FuncError("Ukjent kolonnenavn : {0}".format(self.column_name))
            
      self.new_column_name = self.f.get('nyKolonne')
      if self.new_column_name is None:
        if self.f.get('funksjonsNavn') == 'del_column':
          pass
        else: 
          logger.error("Nytt kolonnenavn er ikke definert")
          raise FuncInvalidConfigError("Nytt kolonnenavn er ikke definert")
            
    return True






