# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 16:41:09 2021

@author: oeh
"""

import pandas as pd
import pathlib
import sys

def reader(file, fileName, logger):
    fileExtension = pathlib.Path(fileName).suffix
    logger.info('Fileextension: {0}'.format(fileExtension))  
    if fileExtension in ('.SAS7BDAT', '.sas7bdat'):
        logger.info('SAS-fil leses inn: {0}'.format(fileName))
        return read_sas(fileName, logger)
    elif fileExtension == '.csv':
        logger.info('csv-fil leses inn: {0}'.format(fileName))
        return read_csv(file, fileName, logger)
    else:
        logger.error('Gyldig filtype ikke oppgitt: {0}'.format(fileName))
        sys.exit(1)
    
def read_sas(fileName, logger):
    try:
        df = pd.read_sas(fileName, format='sas7bdat', index=None, encoding='unicode_escape', chunksize=None, iterator=False)
        return df
    except:
        logger.error('Feil ved lesing av fil: {0}'.format(fileName))
        sys.exit(1)
    
def read_csv(file, fileName, logger):
    delimiter=file.get('sep')
    if delimiter is None:
        logger.error('Skilletegn ikke definert')
        sys.exit(1)
    head=file.get('header')
    if head is None:
        logger.warning('Ikke spesifisert om filen inneholder overskriftsrad')
        head = 0
    encod = file.get('encoding')
    if encod is None:
        logger.error('Encoding ikke definert')
        sys.exit(1)
    
    try:
        df = pd.read_csv(fileName, sep=delimiter, header=int(head), encoding=encod)
        return df
    except:
        logger.error('Feil ved lesing av fil: {0}'.format(fileName))
        sys.exit(1)
    



