from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
import bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import secrets
from flask_bcrypt import Bcrypt
from pyotp import TOTP
import base64
import os


app = Flask(__name__)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/db_name'
app.config['SECRET_KEY'] = 'secret_key'
app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'email@mail.com'
app.config['MAIL_PASSWORD'] = 'password'

db = SQLAlchemy(app)
mail = Mail(app)
bcrypt = Bcrypt(app)




class User(db.Model):
    __tablename__ = 'users'
    email = db.Column(db.String(120), primary_key=True, unique=True)
    password = db.Column(db.String(128), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(128), nullable=True)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class OTPForm(FlaskForm):
    otp = StringField('OTP', validators=[DataRequired()])
    submit = SubmitField('Verify OTP')



@app.route('/')
def start():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please login.', 'danger')
            return redirect(url_for('login'))

        # Generate a valid base32 secret key
        secret_key = base64.b32encode(os.urandom(10)).decode("utf-8").rstrip("=")
        #secret_key = secrets.token_urlsafe(16).rstrip("=")
        totp = TOTP(secret_key)
        otp = totp.now()

        # Save the user to the database with a pending status
        user = User(email=email, password=bcrypt.generate_password_hash(password).decode('utf-8'), verified=False, verification_token=otp)
        db.session.add(user)
        db.session.commit()

        # Send the OTP to the user's email
        try:
            msg = Message('Verify your email', sender='email@mail.com', recipients=[email])
            msg.body = f'Enter the following OTP to complete registration: {otp}'
            mail.send(msg)
            flash('Registration successful. Please enter the OTP to verify your email.', 'success')
        except Exception as e:
            flash('Error sending OTP.', 'danger')
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for('register'))

        return redirect(url_for('verify_otp'))
    return render_template('register.html', form=form)

@app.route('/verify_email/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    if user:
        if user.verified:
            flash('Email already verified.', 'success')
            return redirect(url_for('login'))
        else:
            user.verified = True
            db.session.commit()
            flash('Email verified. You can now login.', 'success')
            return redirect(url_for('login'))
    else:
        flash('Invalid verification token.', 'danger')
        return redirect(url_for('register'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        user = User.query.filter_by(email=email).first()

        
        if user and bcrypt.check_password_hash(user.password, password) and user.verified:
            session['email'] = user.email
            return redirect(url_for('logsuccess'))            
        
        else:
            flash('Login Failed. Check your credentials.', 'danger')
            return redirect(url_for('failedlogin'))

    return render_template('login.html', form=form)

@app.route('/logsuccess')
def logsuccess():
    if 'email' in session:
        u_email = session['email']
        return render_template('homepage.html', email=u_email)
    else:
        flash('You need to login first.', 'danger')
        return redirect(url_for('login'))
    

@app.route('/failedlogin')
def failedlogin():    
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('email', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))




@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    form = OTPForm()
    if form.validate_on_submit():
        otp = form.otp.data
        user = User.query.filter_by(verification_token=otp).first()
        if user:
            user.verified = True
            db.session.commit()
            flash('Email verified. You can now login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP.', 'danger')
            return redirect(url_for('register'))
    return render_template('verify_otp.html', form=form)



if __name__ == "__main__":
    app.run(debug=True)
