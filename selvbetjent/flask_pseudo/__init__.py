from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_pseudo.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'



def create_app(config_class=Config):
  app=Flask(__name__, template_folder='Templates')
  app.config.from_object(Config) 

  db.init_app(app)
  bcrypt.init_app(app)
  login_manager.init_app(app)

  from flask_pseudo.user.routes import users
  from flask_pseudo.log.routes import logs
  from flask_pseudo.main.routes import main
  from flask_pseudo.errors.handlers import errors
  app.register_blueprint(users)
  app.register_blueprint(logs)
  app.register_blueprint(main)
  app.register_blueprint(errors)
  
  return app
