from flask import Blueprint
from flask import request, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from flask_pseudo.models import Log
from flask_pseudo.user.forms import *
from flask_pseudo import bcrypt
from flask_pseudo import db

users = Blueprint('users', __name__)


@users.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
      return redirect(url_for('main.index'))
      
    form = RegistrationForm()

    if form.validate_on_submit():
      hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
      user = User(username=form.username.data, password=hashed_password) 
      db.session.add(user)
      db.session.commit()
      flash(f'Konto opprettet for {form.username.data}!', 'success')
      return redirect(url_for('users.login'))

    return render_template('register.html', title='Register', form=form)


@users.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
      return redirect(url_for('main.index'))
      
    form = LoginForm()
    if form.validate_on_submit():
      user = User.query.filter_by(username=form.username.data).first()
      if user and bcrypt.check_password_hash(user.password, form.password.data):
        login_user(user, remember=form.remember.data)
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main.index'))
      else:
        flash(f'Innlogging feilet. Sjekk brukernavn og passord.', 'danger')
        
    
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

