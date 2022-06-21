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
  
  SSH_HOST = 'localhost'
  SSH_PORT = '5222'
  SSH_TIMEOUT = 10
  HOST = 'localhost'
  PORT = 5000
  SSL = False
  PSEUDO_DB = "pseudo.db"
  PSEUDO_DICT =  {'AUTH' : 'NONE',
    'AUTH_LOCATION' : None, 
    'PSEUDO_ALGORITHM' : 'FF3', #FFX, FF1, FF3
    'OPERATION': 'BOTH', #['BOTH', 'ENCRYPT', 'DECRYPT'],
    'KEY_SOURCE' : 'KEY_LOCATION', #['SQL', 'KEY_LOCATION'],
     'KEY_LOCATION' : 'EF4359D8D580AA4F7F036D6F04FC6A94', 
     'KEY_TYPE': 'FROMHEX', #['STRING', 'BYTES', 'FROMHEX'],
     #Flat dictionary, #SQL cache, inependent cache class, no cache
     'CACHE_SOURCE' : 'SQL', #['DICT', 'SQL', 'NONE'], 
     'CACHE_PARAM' : 100000 #Freetext
     }
