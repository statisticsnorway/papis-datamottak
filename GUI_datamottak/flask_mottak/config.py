import json

with open('/conf/config.json') as config_file:
    config = json.load(config_file)

#TEST lokalt
#with open('./conf/config.json') as config_file:
#    config = json.load(config_file)


class Config:
    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = config.get('SECRET_KEY')
    # list of allowed extensions
    #EXTENSIONS = set(['sas7bdat', 'SAS7BDAT'])
    EXTENSIONS = config.get('EXTENSIONS')
