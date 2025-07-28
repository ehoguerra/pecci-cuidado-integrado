# app/models.py
from app import db, login_manager
from app.utils import encrypt_data, decrypt_data
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Psicologo.query.get(int(user_id))

class Psicologo(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    crp = db.Column(db.String(20), unique=True, nullable=False) # Conselho Regional de Psicologia
    password_hash = db.Column(db.String(128))
    pacientes = db.relationship('Paciente', backref='psicologo', lazy='dynamic', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(150), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=True)
    # Chave estrangeira para ligar o paciente ao psicólogo
    psicologo_id = db.Column(db.Integer, db.ForeignKey('psicologo.id'), nullable=False)
    evolucoes = db.relationship('Evolucao', backref='paciente', lazy='dynamic', cascade="all, delete-orphan")

class Evolucao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_sessao = db.Column(db.DateTime, nullable=False, index=True)
    conteudo_criptografado = db.Column(db.LargeBinary, nullable=False)  # Mudado para LargeBinary para armazenar bytes
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)

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
        """Property para acessar o conteúdo descriptografado"""
        return self.get_conteudo()

    @conteudo.setter
    def conteudo(self, valor):
        """Setter para criptografar automaticamente o conteúdo"""
        self.set_conteudo(valor)