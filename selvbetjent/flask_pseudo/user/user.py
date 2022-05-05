from flask_login import UserMixin
from datetime import datetime

class User(UserMixin):
    userlist = dict()

    def __init__(self, username, ssh, sftp, lastdir):
        self.username = username
        self.created_time = datetime.now()
        self.ssh = ssh
        self.sftp = sftp
        self.lastdir = lastdir
        User.userlist.update({self.username: self})
        
    @classmethod
    def get(cls, username):
        return User.userlist.get(username, None)
    
    @classmethod
    def restart(cls):
        User.userlist = dict()
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return self.is_active
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.username)

