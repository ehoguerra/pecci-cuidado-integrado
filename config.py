import random
import os
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///agendamento.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
APP_SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
APP_NAME = 'Agendamento de Consultas'
APP_VERSION = '1.0.0'
SESSION_COOKIE_NAME = 'session_id'
UPLOAD_FOLDER = 'static/uploads'
SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS=True

# Configurações do Admin
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'change-me')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@sistema.com')

# Configurações de Criptografia
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')