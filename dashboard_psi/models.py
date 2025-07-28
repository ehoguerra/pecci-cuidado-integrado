# dashboard_psi/models.py
"""
Modelos do Dashboard Psicologia adaptados para integração
"""

from db import db
from models.doctors import Doctors
from .utils import encrypt_data, decrypt_data, generate_id
from datetime import datetime


class Paciente(db.Model):
    __tablename__ = 'pacientes'
    
    id = db.Column(db.String(20), primary_key=True, default=generate_id)
    nome_completo = db.Column(db.String(150), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    endereco = db.Column(db.String(200), nullable=True)
    profissao = db.Column(db.String(100), nullable=True)
    estado_civil = db.Column(db.String(50), nullable=True)
    contato_emergencia = db.Column(db.String(200), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    
    # Chave estrangeira para ligar o paciente ao psicólogo
    psicologo_id = db.Column(db.String(20), db.ForeignKey('doctors.id'), nullable=False)
    
    # Relacionamentos
    evolucoes = db.relationship('Evolucao', backref='paciente', lazy='dynamic', cascade="all, delete-orphan")
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = generate_id()
        super(Paciente, self).__init__(**kwargs)

    def __repr__(self):
        return f'<Paciente {self.nome_completo}>'
    
    @property
    def ultima_evolucao(self):
        """Retorna a última evolução do paciente"""
        return self.evolucoes.order_by(Evolucao.data_sessao.desc()).first()


class Evolucao(db.Model):
    __tablename__ = 'evolucoes'
    
    id = db.Column(db.String(20), primary_key=True, default=generate_id)
    data_sessao = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)
    conteudo_criptografado = db.Column(db.LargeBinary, nullable=False)
    tipo_sessao = db.Column(db.String(50), nullable=True)  # Individual, Grupo, etc.
    duracao_minutos = db.Column(db.Integer, nullable=True)
    
    # Chave estrangeira para ligar a evolução ao paciente
    paciente_id = db.Column(db.String(20), db.ForeignKey('pacientes.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = generate_id()
        super(Evolucao, self).__init__(**kwargs)

    def set_conteudo(self, conteudo_texto):
        """Criptografa e armazena o conteúdo da evolução"""
        self.conteudo_criptografado = encrypt_data(conteudo_texto)

    def get_conteudo(self):
        """Descriptografa e retorna o conteúdo da evolução"""
        if self.conteudo_criptografado:
            return decrypt_data(self.conteudo_criptografado)
        return ""

    @property
    def conteudo(self):
        """Property para facilitar acesso ao conteúdo descriptografado"""
        return self.get_conteudo()

    @conteudo.setter
    def conteudo(self, value):
        """Property setter para facilitar atribuição do conteúdo"""
        self.set_conteudo(value)

    def __repr__(self):
        return f'<Evolucao {self.id} - {self.data_sessao}>'
    
class Agenda(db.Model):
    __tablename__ = 'agenda'
    
    id = db.Column(db.String(20), primary_key=True, default=generate_id)
    paciente_id = db.Column(db.String(20), db.ForeignKey('pacientes.id'), nullable=False)
    psicologo_id = db.Column(db.String(20), db.ForeignKey('doctors.id'), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False, index=True)
    compromissos = db.Column(db.String(200), nullable=True)  # Descrição dos compromissos
    local = db.Column(db.String(200), nullable=True)  # Local da consulta
    observacoes = db.Column(db.Text, nullable=True)  # Observações adicionais
    
    # Status da consulta
    status = db.Column(db.String(50), default='agendada')  # agendada, confirmada, cancelada, concluída
    
    # Campos para recorrência
    recorrente = db.Column(db.Boolean, default=False)  # Se é agendamento recorrente
    recorrencia_tipo = db.Column(db.String(20), nullable=True)  # 'semanal', 'quinzenal', 'mensal'
    recorrencia_periodo = db.Column(db.String(20), nullable=True)  # '3meses', '6meses', '1ano'
    recorrencia_grupo_id = db.Column(db.String(20), nullable=True)  # ID para agrupar agendamentos recorrentes
    agenda_pai_id = db.Column(db.String(20), db.ForeignKey('agenda.id'), nullable=True)  # Agendamento original
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Relacionamentos
    paciente = db.relationship('Paciente', backref='agendamentos')
    psicologo = db.relationship('Doctors', backref='agendamentos', foreign_keys=[psicologo_id])
    
    # Relacionamento para agendamentos filhos (recorrentes)
    agendamentos_filhos = db.relationship('Agenda', backref=db.backref('agenda_pai', remote_side='Agenda.id'))

    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = generate_id()
        super(Agenda, self).__init__(**kwargs)

    @property
    def status_color(self):
        """Retorna a cor do status para exibição"""
        colors = {
            'agendada': 'primary',
            'confirmada': 'success',
            'cancelada': 'danger',
            'concluida': 'secondary'
        }
        return colors.get(self.status, 'primary')

    @property
    def status_text(self):
        """Retorna o texto formatado do status"""
        texts = {
            'agendada': 'Agendada',
            'confirmada': 'Confirmada',
            'cancelada': 'Cancelada',
            'concluida': 'Concluída'
        }
        return texts.get(self.status, 'Agendada')
    
    @property
    def recorrencia_texto(self):
        """Retorna texto descritivo da recorrência"""
        if not self.recorrente:
            return None
            
        tipo_texto = {
            'semanal': 'Semanal',
            'quinzenal': 'Quinzenal',
            'mensal': 'Mensal'
        }.get(self.recorrencia_tipo, '')
        
        periodo_texto = {
            '3meses': '3 meses',
            '6meses': '6 meses',
            '1ano': '1 ano'
        }.get(self.recorrencia_periodo, '')
        
        return f"{tipo_texto} por {periodo_texto}"
    
    def get_total_agendamentos_grupo(self):
        """Retorna o total de agendamentos no grupo de recorrência"""
        if not self.recorrencia_grupo_id:
            return 1
        
        return Agenda.query.filter_by(recorrencia_grupo_id=self.recorrencia_grupo_id).count()

    def __repr__(self):
        return f'<Agenda {self.id} - {self.data_hora}>'