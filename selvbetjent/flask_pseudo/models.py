#from flask_login import UserMixin
from datetime import datetime

from .create_app import db
#from .create_app import login_manager

#@login_manager.user_loader
#def load_user(user_id):
#  return User.query.get(int(user_id))
#
#class User(db.Model, UserMixin):
#    id = db.Column(db.Integer, primary_key=True)
#    username = db.Column(db.String(20), unique=True, nullable=False)
#    password = db.Column(db.String(60), nullable=False)
#    rapporter = db.relationship('Log', backref='author', lazy=True)
#    
#    def __repr__(self):
#        return f"User('{self.username}')"

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kildefil = db.Column(db.String(200), nullable=False)
    pseudo_var = db.Column(db.String(200))
    delete_var = db.Column(db.String(200))
    resultatfil = db.Column(db.String(200), nullable=False)
    dato_opprettet = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f"Log('{self.kildefil}', '{self.pseudo_var}', '{self.delete_var}', '{self.resultatfil}')"
	
