import random
import os
DEBUG = True
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123911ar@localhost/consultas'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.urandom(24)
APP_SECRET_KEY = os.urandom(24)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
APP_NAME = 'Agendamento de Consultas'
APP_VERSION = '1.0.0'
SESSION_COOKIE_NAME = 'session_id'
UPLOAD_FOLDER = 'static/uploads'