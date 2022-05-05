from string import ascii_letters, digits
from random import SystemRandom


class Config:
  SQLALCHEMY_DATABASE_URI = 'sqlite:///bruker.db'
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  #maximum filesize in megabytes
  #file_mb_max = 100
  #encryption kew
  #SECRET_KEY='key'
  SECRET_KEY = ''.join(SystemRandom().choice(
      ascii_letters + digits) for _ in range(32))
  #list of allowed extensions
  EXTENSIONS = set(['sas7bdat','SAS7BDAT'])
  #extensions = set(['txt','sas7bdat','SAS7BDAT','json', 'csv'])

