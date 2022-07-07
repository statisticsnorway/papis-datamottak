import json, sys

#
conf = './' if sys.platform == 'win32' else '/conf/'
file = conf + 'config.json'
with open(file) as config_file:
    config = json.load(config_file)


class Config:
    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = config.get('SECRET_KEY')
    # list of allowed extensions
    #EXTENSIONS = set(['sas7bdat', 'SAS7BDAT'])
    EXTENSIONS = config.get('EXTENSIONS')
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
