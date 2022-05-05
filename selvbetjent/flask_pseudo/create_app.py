from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

from .config import Config

from datamottak.sftp.sftpserver import start_server, stop_server

import threading
import sys

db = SQLAlchemy()
migrate = Migrate()

bcrypt = Bcrypt()
root = 'C:/' if sys.platform == 'win32' else '/ssb/'
#Placeholder for:
#with open('config_mal.json', 'r') as myfile:
#  data=json.loads(myfile.read())
data = None


def startAll():
  start_server()
  app = create_app()
  return app

def stopAll(app):
  stop_server()

def create_app(config_class=Config):
  app=Flask(__name__, template_folder='Templates')
  app.config.from_object(Config)

  db.init_app(app)
  migrate.init_app(app, db)
  bcrypt.init_app(app)
  
  app.jinja_env.trim_blocks = True
  app.jinja_env.lstrip_blocks = True
  
  from .user.routes import login_manager
  
  login_manager.init_app(app)
  
  #with open('config_mal.json', 'r') as myfile:
  #  data=json.loads(myfile.read())
  dictionary = {'db': db, 'migrate': migrate, 'bcrypt': bcrypt, 
                'login_manager' : login_manager,
                'data' : data, 'root' : root}
  app.config['PAPIS'] = dictionary

  from .user.routes import users
  from .log.routes import logs
  from .main.routes import main
  from .main.routes_dev import dev
  from .errors.handlers import errors
  
  app.register_blueprint(users)
  app.register_blueprint(logs)
  app.register_blueprint(main)
  app.register_blueprint(dev)
  app.register_blueprint(errors)
  
  return app

def customRun(app, threaded=True, host='localhost', port = 5000): 
  if threaded:
    thread = threading.Thread(target=app.run, 
                name='Flask server thread',
                kwargs={'host':host, 'port':port} )
    thread.app = app
    thread.start()
  else:
    app.run(host = host, port = port)

    




