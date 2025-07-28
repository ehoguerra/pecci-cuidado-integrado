from cryptography.fernet import Fernet
from flask import current_app

def encrypt_data(data_string: str) -> bytes:
    """Criptografa uma string e retorna o resultado em bytes."""
    try:
        key = current_app.config['ENCRYPTION_KEY'].encode('utf-8')
        f = Fernet(key)
        return f.encrypt(data_string.encode('utf-8'))
    except Exception as e:
        current_app.logger.error(f"Erro ao criptografar dados: {e}")
        return None

def decrypt_data(encrypted_bytes: bytes) -> str:
    """Descriptografa bytes e retorna o resultado em uma string."""
    try:
        key = current_app.config['ENCRYPTION_KEY'].encode('utf-8')
        f = Fernet(key)
        return f.decrypt(encrypted_bytes).decode('utf-8')
    except Exception as e:
        current_app.logger.error(f"Erro ao descriptografar dados: {e}")
        return "Erro: não foi possível descriptografar os dados."