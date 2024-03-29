from datetime import datetime
from flask import render_template, flash, redirect, url_for
from flask import request
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user
from flask_login import login_required

from app.models import User, Question, Answer, Annotation
from app import app
from app import db
from .forms import LoginForm, RegistrationForm


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()



@app.route('/')
@app.route('/index')
@login_required
def index():
    """ Main page """
    return render_template('index.html')


@app.route('/user/<username>')
@login_required
def user(username):
    """ User profile page """
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@app.route('/questions')
@login_required
def question():
    """ question page """

    # list all the questions
    questions = Question.query.all()

    return render_template('questions.html', questions=questions)



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        
        # check if the request is redirected by flask_login
        # which will be included in the url, such as /login?next=/index
        next_page = request.args.get('next')        
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congradulations, you are now a registered user!')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))