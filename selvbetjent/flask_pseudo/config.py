import os

class Config:
  SQLALCHEMY_DATABASE_URI = 'sqlite:///bruker.db'
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  #maximum filesize in megabytes
  #file_mb_max = 100
  #encryption kew
  SECRET_KEY='key'
  #list of allowed extensions
  EXTENSIONS = set(['sas7bdat','SAS7BDAT'])
  #extensions = set(['txt','sas7bdat','SAS7BDAT','json', 'csv'])

