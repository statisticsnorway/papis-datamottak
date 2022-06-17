from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from flask_mottak.config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__, template_folder='Templates')
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    app.app_context().push()

    from flask_mottak.leverandorer.routes import leverandorer
    from flask_mottak.dataleveranse.routes import dataleveranser
    from flask_mottak.periodeleveranser.routes import periodeleveranser
    from flask_mottak.main.routes import main
    from flask_mottak.fil.routes import fil
    from flask_mottak.errors.handlers import errors
    app.register_blueprint(leverandorer)
    app.register_blueprint(dataleveranser)
    app.register_blueprint(periodeleveranser)
    app.register_blueprint(main)
    app.register_blueprint(fil)
    app.register_blueprint(errors)

    return app
