from cryptography.fernet import Fernet
from flask import current_app
import os
import secrets

def get_or_create_encryption_key():
    """Gera ou recupera a chave de criptografia do .env ou arquivo"""
    # Primeira tentativa: usar chave do .env
    if hasattr(current_app, 'config') and 'ENCRYPTION_KEY' in current_app.config and current_app.config['ENCRYPTION_KEY']:
        return current_app.config['ENCRYPTION_KEY'].encode('utf-8')
    
    # Segunda tentativa: usar arquivo de chave local
    key_file = 'encryption.key'
    
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            return f.read()
    else:
        # Gerar nova chave e salvar no arquivo (fallback)
        key = Fernet.generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
        if hasattr(current_app, 'logger'):
            current_app.logger.warning("Chave de criptografia gerada localmente - configure ENCRYPTION_KEY no .env para produção!")
        return key

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
        # Tentar retornar como string se não conseguir descriptografar
        try:
            return encrypted_bytes.decode('utf-8')
        except:
            return "Erro: não foi possível descriptografar os dados."

def generate_id():
    """Gera um ID único para os registros"""
    return secrets.token_urlsafe(16)[:20]

def nl2br(text):
    """Converte quebras de linha em tags <br>"""
    if not text:
        return ""
    return text.replace('\n', '<br>\n').replace('\r\n', '<br>\r\n')

def calcular_agendamentos_recorrentes(data_inicial, tipo_recorrencia, periodo_recorrencia):
    """
    Calcula todas as datas para agendamentos recorrentes
    
    Args:
        data_inicial (datetime): Data/hora do primeiro agendamento
        tipo_recorrencia (str): 'semanal', 'quinzenal', 'mensal'
        periodo_recorrencia (str): '3meses', '6meses', '1ano'
    
    Returns:
        list: Lista de datetimes para os agendamentos
    """
    from datetime import datetime, timedelta
    from dateutil.relativedelta import relativedelta
    
    agendamentos = [data_inicial]
    
    # Definir intervalos
    intervalos = {
        'semanal': timedelta(weeks=1),
        'quinzenal': timedelta(weeks=2),
        'mensal': relativedelta(months=1)
    }
    
    # Definir duração total
    duracoes = {
        '3meses': relativedelta(months=3),
        '6meses': relativedelta(months=6),
        '1ano': relativedelta(years=1)
    }
    
    if tipo_recorrencia not in intervalos or periodo_recorrencia not in duracoes:
        return agendamentos
    
    data_limite = data_inicial + duracoes[periodo_recorrencia]
    data_atual = data_inicial
    
    while True:
        if tipo_recorrencia == 'mensal':
            data_atual = data_atual + intervalos[tipo_recorrencia]
        else:
            data_atual = data_atual + intervalos[tipo_recorrencia]
        
        if data_atual > data_limite:
            break
            
        agendamentos.append(data_atual)
    
    return agendamentos

def criar_agendamentos_recorrentes(paciente_id, psicologo_id, data_hora_inicial, 
                                  compromissos, local, observacoes, status,
                                  recorrencia_tipo, recorrencia_periodo):
    """
    Cria uma série de agendamentos recorrentes
    
    Args:
        paciente_id (str): ID do paciente
        psicologo_id (str): ID do psicólogo
        data_hora_inicial (datetime): Data e hora inicial
        compromissos (str): Descrição dos compromissos
        local (str): Local da consulta
        observacoes (str): Observações
        status (str): Status do agendamento
        recorrencia_tipo (str): Tipo de recorrência
        recorrencia_periodo (str): Período de recorrência
    
    Returns:
        list: Lista de agendamentos criados
    """
    from .models import Agenda
    from db import db
    
    # Calcular todas as datas
    datas_agendamentos = calcular_agendamentos_recorrentes(
        data_hora_inicial,
        recorrencia_tipo,
        recorrencia_periodo
    )
    
    # Gerar ID do grupo de recorrência
    grupo_id = generate_id()
    agendamentos_criados = []
    
    for i, data_hora in enumerate(datas_agendamentos):
        agenda = Agenda(
            paciente_id=paciente_id,
            psicologo_id=psicologo_id,
            data_hora=data_hora,
            compromissos=compromissos,
            local=local,
            observacoes=observacoes,
            status=status,
            recorrente=True,
            recorrencia_tipo=recorrencia_tipo,
            recorrencia_periodo=recorrencia_periodo,
            recorrencia_grupo_id=grupo_id,
            agenda_pai_id=None if i == 0 else agendamentos_criados[0].id
        )
        
        db.session.add(agenda)
        agendamentos_criados.append(agenda)
    
    # Definir o primeiro como pai dos outros
    if len(agendamentos_criados) > 1:
        for agenda in agendamentos_criados[1:]:
            agenda.agenda_pai_id = agendamentos_criados[0].id
    
    db.session.commit()
    
    return agendamentos_criados
