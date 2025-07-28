# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import Psicologo, Paciente, Evolucao
from app.forms import LoginForm, PacienteForm, EvolucaoForm
from app.utils import encrypt_data, decrypt_data
from flask_login import current_user, login_user, logout_user, login_required

bp = Blueprint('main', __name__)

# --- Rotas de Autenticação ---
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        psicologo = Psicologo.query.filter_by(email=form.email.data).first()
        if psicologo and psicologo.check_password(form.password.data):
            login_user(psicologo, remember=form.remember_me.data)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha inválidos.', 'danger')
    
    return render_template('login.html', title='Login', form=form)
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# --- Rotas Principais (requerem login) ---

@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))
    pacientes = Paciente.query.filter_by(psicologo_id=current_user.id).order_by(Paciente.nome_completo).all()
    return render_template('dashboard.html', title='Dashboard', pacientes=pacientes)

@bp.route('/paciente/<int:paciente_id>')
@login_required
def perfil_paciente(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    # VERIFICAÇÃO DE SEGURANÇA CRÍTICA: O psicólogo só pode ver seus próprios pacientes.
    if paciente.psicologo_id != current_user.id:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    evolucoes = paciente.evolucoes.order_by(Evolucao.data_sessao.desc()).all()
    return render_template('perfil_paciente.html', paciente=paciente, evolucoes=evolucoes)

@bp.route('/paciente/novo', methods=['GET', 'POST'])
@login_required
def novo_paciente():
    form = PacienteForm()
    if form.validate_on_submit():
        paciente = Paciente(nome_completo=form.nome_completo.data, psicologo_id=current_user.id)
        db.session.add(paciente)
        db.session.commit()
        flash('Paciente registrado com sucesso!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('form_paciente.html', title='Novo Paciente', form=form)

# ... Rotas para adicionar/editar evoluções ...

@bp.route('/paciente/<int:paciente_id>/evolucao/nova', methods=['GET', 'POST'])
@login_required
def nova_evolucao(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    # Verificação de segurança
    if paciente.psicologo_id != current_user.id:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = EvolucaoForm()
    if form.validate_on_submit():
        evolucao = Evolucao(
            data_sessao=form.data_sessao.data,
            paciente_id=paciente.id
        )
        # Usar o setter para criptografar automaticamente
        evolucao.conteudo = form.conteudo.data
        
        if evolucao.conteudo_criptografado is None:
            flash('Erro ao criptografar dados. Tente novamente.', 'danger')
            return render_template('form_evolucao.html', title='Nova Evolução', form=form, paciente=paciente)
        
        db.session.add(evolucao)
        db.session.commit()
        flash('Evolução registrada com sucesso!', 'success')
        return redirect(url_for('main.perfil_paciente', paciente_id=paciente.id))
    
    return render_template('form_evolucao.html', title='Nova Evolução', form=form, paciente=paciente)

@bp.route('/evolucao/<int:evolucao_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_evolucao(evolucao_id):
    evolucao = Evolucao.query.get_or_404(evolucao_id)
    # Verificação de segurança dupla
    if evolucao.paciente.psicologo_id != current_user.id:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = EvolucaoForm()
    if form.validate_on_submit():
        evolucao.data_sessao = form.data_sessao.data
        # Usar o setter para criptografar automaticamente
        evolucao.conteudo = form.conteudo.data
        
        if evolucao.conteudo_criptografado is None:
            flash('Erro ao criptografar dados. Tente novamente.', 'danger')
            return render_template('form_evolucao.html', title='Editar Evolução', form=form, paciente=evolucao.paciente, evolucao=evolucao)
        
        db.session.commit()
        flash('Evolução atualizada com sucesso!', 'success')
        return redirect(url_for('main.perfil_paciente', paciente_id=evolucao.paciente_id))
    elif request.method == 'GET':
        form.data_sessao.data = evolucao.data_sessao
        # Usar o getter para descriptografar automaticamente
        form.conteudo.data = evolucao.conteudo
    
    return render_template('form_evolucao.html', title='Editar Evolução', form=form, paciente=evolucao.paciente, evolucao=evolucao)