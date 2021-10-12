# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 16:41:09 2021

@author: oeh
"""

import pandas as pd
import pathlib
import sys
import glob
import os

class Reader:

  def reader(self, file, fileName, logger):
    self.fileExtension = pathlib.Path(fileName).suffix
    logger.info('Fileextension: {0}'.format(self.fileExtension))  
    if self.fileExtension in ('.SAS7BDAT', '.sas7bdat'):
      logger.info('SAS-fil leses inn: {0}'.format(fileName))
      return self.read_sas(fileName, logger)
    elif self.fileExtension == '.csv':
      logger.info('csv-fil leses inn: {0}'.format(fileName))
      return self.read_csv(file, fileName, logger)
    else:
      logger.error('Gyldig filtype ikke oppgitt: {0}'.format(fileName))
      sys.exit(1)

  def getExtension(self, fileName, logger):
    self.fileExtension = pathlib.Path(fileName).suffix
    logger.info('Fileextension: {0}'.format(self.fileExtension))  
    if self.fileExtension in ('.SAS7BDAT', '.sas7bdat'):
      logger.info('SAS-fil leses inn: {0}'.format(fileName))
    elif self.fileExtension == '.csv':
      logger.info('csv-fil leses inn: {0}'.format(fileName))
    else:
      logger.error('Gyldig filtype ikke oppgitt: {0}'.format(fileName))
      sys.exit(1)

    return self.fileExtension      
 
  def read_sas(self, fileName, logger):
    try:
      self.df = pd.read_sas(fileName, format='sas7bdat', index=None, encoding='unicode_escape', chunksize=None, iterator=False)
      return self.df
    except:
      logger.error('Feil ved lesing av fil: {0}'.format(fileName))
      sys.exit(1)
    
  def read_csv(self,file, fileName, logger):
    self.delimiter=file.get('sep')
    if self.delimiter is None:
      logger.error('Skilletegn ikke definert')
      sys.exit(1)
    self.head=file.get('header')
    if self.head is None:
      logger.warning('Ikke spesifisert om filen inneholder overskriftsrad')
      self.head = 0
    self.encod = file.get('encoding')
    if self.encod is None:
      logger.error('Encoding ikke definert')
      sys.exit(1)
    
    try:
      self.df = pd.read_csv(fileName, sep=self.delimiter, header=int(self.head), encoding=self.encod)
      return self.df
    except:
      logger.error('Feil ved lesing av fil: {0}'.format(fileName))
      sys.exit(1)
    

#Legger filnavn i dictionary. Ønsker at oppgitt filnavn ikke trenger å være case-sensitiv
  def getFileNameWithLowerCase(self, filename):
    self.file_names_dict = {}
    for f in glob.glob(os.path.dirname(filename)+'//*.csv'):
      self.file_names_dict[os.path.basename(f).lower()] = f
    for f in glob.glob(os.path.dirname(filename)+'//*.sas7bdat'):
      self.file_names_dict[os.path.basename(f).lower()] = f
    
    return self.file_names_dict




