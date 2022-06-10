from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

from .config import Config
from .pseudoService import PseudoService

from datamottak.sftp.sftpserver import start_server, stop_server
from papis_service.common.configureServerEnv import ConfigureServerEnv

import threading
import sys

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

root = 'C:/' if sys.platform == 'win32' else '/ssb/'



def startAll():
  start_server()
  app = create_app()
  return app

def stopAll(app):
  stop_server()

def create_app(config_class=Config):
  app=Flask(__name__, template_folder='Templates')
  app.config.from_object(config_class)

  db.init_app(app)
  migrate.init_app(app, db)
  bcrypt.init_app(app)
  
  app.jinja_env.trim_blocks = True
  app.jinja_env.lstrip_blocks = True
  
  pseudoService = PseudoService(app.config['PSEUDO_DB'], app.config['PSEUDO_DICT'],
                            'papisService', app.instance_path)

  from .user.routes import login_manager
  
  login_manager.init_app(app)
  
  #with open('config_mal.json', 'r') as myfile:
  #  data=json.loads(myfile.read())
  dictionary = {'db': db, 'migrate': migrate, 'bcrypt': bcrypt, 
                'login_manager' : login_manager,
                'root' : root}
  app.config['PAPIS'] = dictionary
  app.config['PSEUDO'] = pseudoService
  ssh_host = app.config['SSH_HOST']
  ssh_port = app.config['SSH_PORT']
  ssh_timeout = app.config['SSH_TIMEOUT']
  
  from .user.routes import users
  from .log.routes import logs
  from .main.routes import main
  from .main.routes_dev import dev
  from .errors.handlers import errors
  
  with app.app_context():
      app.register_blueprint(users)
      app.register_blueprint(logs)
      app.register_blueprint(main)
      app.register_blueprint(dev)
      app.register_blueprint(errors)
      current_app.pseudoService = pseudoService
      current_app.bcrypt = bcrypt
      current_app.db = db
      current_app.ssh_host = ssh_host
      current_app.ssh_port = ssh_port
      current_app.ssh_timeout = ssh_timeout
  
  return app

def customRun(app, server=True,  threaded=True, host=None, port = None):
   host = host if host else app.config.get('HOST')
   port = port if port else app.config.get('PORT')
   if not host or not port:
     raise ValueError('host or port not set')
   if threaded:  
     thread = threading.Thread(target=app.run, 
                name='Flask server thread',
                kwargs={'host':host, 'port':port} )
     thread.app = app
     thread.start()
   else:
     app.run(host = host, port = port)

    




