from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_login import current_user
from flask import flash, redirect, url_for, render_template

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Manter-me conectado')

    submit = SubmitField('Entrar')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    confirm_password = PasswordField('Confirme a Senha', validators=[DataRequired(), EqualTo('password')])
    remember_me = BooleanField('Manter-me conectado')

    submit = SubmitField('Registrar')

class PacienteForm(FlaskForm):
    nome_completo = StringField('Nome Completo', validators=[DataRequired(), Length(max=150)])
    data_nascimento = DateField('Data de Nascimento', format='%Y-%m-%d', validators=[DataRequired()])
    
    submit = SubmitField('Salvar Paciente')

class EvolucaoForm(FlaskForm):
    conteudo = TextAreaField('Conteúdo da Evolução', validators=[DataRequired(), Length(max=2000)])
    data_sessao = DateField('Data da Sessão', format='%Y-%m-%d', validators=[DataRequired()])
    
    submit = SubmitField('Salvar Evolução')