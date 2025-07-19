import bcrypt
import uuid
from db import db
from models.user import User
from models.doctors import Doctors
from flask import session, redirect, render_template

def login_user(email, password):
    user = db.session.query(User).filter_by(email=email).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        session['user_id'] = user.id
        return redirect('/app')
    return render_template('login.html', error='E-mail ou senha inválidos')

def register_user(email, name, password, birth_date, phone_number):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(
        id=str(uuid.uuid4().fields[-1])[:20],
        email=email,
        name=name,
        password=hashed_password.decode('utf-8'),
        birth_date=birth_date,
        phone_number=phone_number
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user