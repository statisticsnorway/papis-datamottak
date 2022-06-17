from flask import Blueprint
from flask import request, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from ..models import Log
from .forms import LoginForm
from .user import User
import paramiko
import socket
from flask_login import LoginManager

users = Blueprint('users', __name__)
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    print(f'User loader: {user_id} {User.get(user_id)}')
    return User.get(user_id)

@users.before_app_first_request
def init_users():
    if not all(hasattr(current_app, attr) for attr 
               in ['ssh_host', 'ssh_port', 'ssh_timeout']):
        raise AttributeError('users: current_app missing variables')
    User.restart()

@users.route('/login', methods=['POST', 'GET'])
def login():
    #if not current_user.is_authenticated:
    #    if current_user.sftp.get_transport.active:
    #        return redirect(url_for('main.index'))
    #    else: 
    #        logout_user()
    #        flash('sftp connection lost, user logged out', 'danger')
        
    if current_user.is_authenticated:
      return redirect(url_for('main.index'))
      
    form = LoginForm()
    if form.validate_on_submit():
      #print ('form.validate')
      ssh = paramiko.SSHClient()
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      try:
          #print(f'{current_app.host}, {current_app.port},',
          #      f'{current_app.timeout}, {form.username.data}',
          #      f'{form.password.data}')
          ssh.connect(current_app.ssh_host, 
                port = current_app.ssh_port, 
                timeout = current_app.ssh_timeout, 
                username = form.username.data, 
                password = form.password.data)
          sftp = ssh.open_sftp()
          sftp.chdir('/')
          lastdir = sftp.listdir_attr() #Get content of root
          user = User(form.username.data, ssh, sftp, lastdir)  
          login_user(user)
          next_page = request.args.get('next')
          return redirect(next_page) if next_page else redirect(url_for('main.index'))
      except paramiko.BadHostKeyException:
          flash('BadHostKeyException, kobling til filsystem ikke mulig', 'danger')
      except paramiko.AuthenticationException:
          flash('Innlogging feilet. Sjekk brukernavn og passord.', 'danger')
      except paramiko.SSHException:
          flash('SSHException, kobling til filsystem ikke mulig', 'danger')
      except socket.error:
          flash('socket.error, kobling til filsystem ikke mulig', 'danger')

    return render_template('login.html', title='Login', form=form)



@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
   

@users.route('/account')
@login_required 
def account():
    return render_template('account.html', title='Account')
 

@users.route('/user/<string:username>', methods=['POST', 'GET'])   
@login_required
def user_log(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    logs = Log.query.filter_by(author=user)\
      .order_by(Log.dato_opprettet.desc())\
      .paginate(page=page, per_page=2)
    #logs = Log.query.order_by(Log.dato_opprettet.desc()).paginate(page=page, per_page=2)
    

    return render_template('user_logs.html', logs = logs, user=user, title='Log')

