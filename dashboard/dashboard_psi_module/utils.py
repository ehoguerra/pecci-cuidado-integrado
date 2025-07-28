from cryptography.fernet import Fernet
from flask import current_app

def encrypt_data(data_string: str) -> bytes:
    """Criptografa uma string e retorna o resultado em bytes."""
    try:
        # Usar chave do arquivo de configuração (.env)
        if hasattr(current_app, 'config') and 'ENCRYPTION_KEY' in current_app.config and current_app.config['ENCRYPTION_KEY']:
            key = current_app.config['ENCRYPTION_KEY'].encode('utf-8')
        else:
            # Fallback para chave padrão em desenvolvimento (não recomendado para produção)
            key = b'ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg='
            if hasattr(current_app, 'logger'):
                current_app.logger.warning("Usando chave de criptografia padrão - configure ENCRYPTION_KEY no .env para produção!")
        
        f = Fernet(key)
        return f.encrypt(data_string.encode('utf-8'))
    except Exception as e:
        if hasattr(current_app, 'logger'):
            current_app.logger.error(f"Erro ao criptografar dados: {e}")
        print(f"Erro ao criptografar dados: {e}")
        return data_string.encode('utf-8')  # Fallback sem criptografia

def decrypt_data(encrypted_bytes: bytes) -> str:
    """Descriptografa bytes e retorna o resultado em uma string."""
    try:
        # Usar chave do arquivo de configuração (.env)
        if hasattr(current_app, 'config') and 'ENCRYPTION_KEY' in current_app.config and current_app.config['ENCRYPTION_KEY']:
            key = current_app.config['ENCRYPTION_KEY'].encode('utf-8')
        else:
            # Fallback para chave padrão em desenvolvimento (não recomendado para produção)
            key = b'ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg='
            if hasattr(current_app, 'logger'):
                current_app.logger.warning("Usando chave de criptografia padrão - configure ENCRYPTION_KEY no .env para produção!")
        
        f = Fernet(key)
        return f.decrypt(encrypted_bytes).decode('utf-8')
    except Exception as e:
        if hasattr(current_app, 'logger'):
            current_app.logger.error(f"Erro ao descriptografar dados: {e}")
        print(f"Erro ao descriptografar dados: {e}")
        return "Erro: não foi possível descriptografar os dados."