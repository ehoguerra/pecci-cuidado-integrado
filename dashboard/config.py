import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(32))

    DEBUG = True
    LOGIN_DISABLED = False

    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')  

    if not ENCRYPTION_KEY:
        # Gerar uma chave padrão para desenvolvimento se não estiver definida
        from cryptography.fernet import Fernet
        ENCRYPTION_KEY = Fernet.generate_key().decode()
        print("⚠️  Usando chave de criptografia gerada automaticamente. Configure ENCRYPTION_KEY em produção!")
