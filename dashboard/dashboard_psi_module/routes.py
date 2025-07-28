# dashboard_psi/routes.py
"""
Rotas do Dashboard Psicologia adaptadas para integração
"""

from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from . import bp
from .models import Paciente, Evolucao
from .forms import PacienteForm, EvolucaoForm
from .utils import encrypt_data, decrypt_data
from app import db
from functools import wraps

def psicologo_required(f):
    """Decorator para verificar se o usuário é psicólogo"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        # Verificar se é psicólogo (adapte conforme seu modelo User)
        if not hasattr(current_user, 'crp') or not current_user.crp:
            flash('Acesso restrito a psicólogos cadastrados.', 'warning')
            abort(403)
            
        return f(*args, **kwargs)
    return decorated_function

# --- Dashboard Principal ---
@bp.route('/')
@psicologo_required
def dashboard():
    """Dashboard principal do módulo"""
    # Buscar pacientes do psicólogo atual
    pacientes = Paciente.query.filter_by(psicologo_id=current_user.id).all()
    
    # Estatísticas
    total_pacientes = len(pacientes)
    total_evolucoes = sum(len(p.evolucoes) for p in pacientes)
    
    # Últimas evoluções
    ultimas_evolucoes = (Evolucao.query
                        .join(Paciente)
                        .filter(Paciente.psicologo_id == current_user.id)
                        .order_by(Evolucao.data_sessao.desc())
                        .limit(5)
                        .all())
    
    return render_template('dashboard_psi/dashboard.html',
                         title='Dashboard Psicologia',
                         pacientes=pacientes,
                         total_pacientes=total_pacientes,
                         total_evolucoes=total_evolucoes,
                         ultimas_evolucoes=ultimas_evolucoes)

# --- Rotas de Pacientes ---
@bp.route('/pacientes')
@psicologo_required
def listar_pacientes():
    """Lista todos os pacientes do psicólogo"""
    search = request.args.get('search', '')
    
    query = Paciente.query.filter_by(psicologo_id=current_user.id)
    
    if search:
        query = query.filter(Paciente.nome_completo.contains(search))
    
    pacientes = query.order_by(Paciente.nome_completo).all()
    
    return render_template('dashboard_psi/listar_pacientes.html',
                         title='Pacientes',
                         pacientes=pacientes,
                         search=search)

@bp.route('/pacientes/novo', methods=['GET', 'POST'])
@psicologo_required
def novo_paciente():
    """Cadastrar novo paciente"""
    form = PacienteForm()
    
    if form.validate_on_submit():
        paciente = Paciente(
            nome_completo=form.nome_completo.data,
            data_nascimento=form.data_nascimento.data,
            telefone=form.telefone.data,
            email=form.email.data,
            endereco=form.endereco.data,
            profissao=form.profissao.data,
            estado_civil=form.estado_civil.data,
            contato_emergencia=form.contato_emergencia.data,
            observacoes=form.observacoes.data,
            psicologo_id=current_user.id
        )
        
        db.session.add(paciente)
        db.session.commit()
        
        flash(f'Paciente {paciente.nome_completo} cadastrado com sucesso!', 'success')
        return redirect(url_for('dashboard_psi.perfil_paciente', id=paciente.id))
    
    return render_template('dashboard_psi/form_paciente.html',
                         title='Novo Paciente',
                         form=form)

@bp.route('/pacientes/<int:id>')
@psicologo_required
def perfil_paciente(id):
    """Perfil do paciente com histórico de evoluções"""
    paciente = Paciente.query.filter_by(
        id=id, 
        psicologo_id=current_user.id
    ).first_or_404()
    
    # Buscar evoluções com paginação
    page = request.args.get('page', 1, type=int)
    evolucoes = (Evolucao.query
                .filter_by(paciente_id=paciente.id)
                .order_by(Evolucao.data_sessao.desc())
                .paginate(
                    page=page, 
                    per_page=10, 
                    error_out=False
                ))
    
    return render_template('dashboard_psi/perfil_paciente.html',
                         title=f'Paciente: {paciente.nome_completo}',
                         paciente=paciente,
                         evolucoes=evolucoes)

# --- Rotas de Evoluções ---
@bp.route('/pacientes/<int:paciente_id>/evolucoes/nova', methods=['GET', 'POST'])
@psicologo_required
def nova_evolucao(paciente_id):
    """Criar nova evolução para o paciente"""
    paciente = Paciente.query.filter_by(
        id=paciente_id,
        psicologo_id=current_user.id
    ).first_or_404()
    
    form = EvolucaoForm()
    
    if form.validate_on_submit():
        evolucao = Evolucao(
            data_sessao=form.data_sessao.data,
            paciente_id=paciente.id
        )
        # Usar criptografia automática
        evolucao.conteudo = form.conteudo.data
        
        db.session.add(evolucao)
        db.session.commit()
        
        flash('Evolução registrada com sucesso!', 'success')
        return redirect(url_for('dashboard_psi.perfil_paciente', id=paciente.id))
    
    # Pré-preencher data de hoje
    if not form.data_sessao.data:
        from datetime import datetime
        form.data_sessao.data = datetime.now()
    
    return render_template('dashboard_psi/form_evolucao.html',
                         title='Nova Evolução',
                         form=form,
                         paciente=paciente)

@bp.route('/evolucoes/<int:id>/editar', methods=['GET', 'POST'])
@psicologo_required
def editar_evolucao(id):
    """Editar evolução existente"""
    evolucao = Evolucao.query.join(Paciente).filter(
        Evolucao.id == id,
        Paciente.psicologo_id == current_user.id
    ).first_or_404()
    
    form = EvolucaoForm(obj=evolucao)
    
    if form.validate_on_submit():
        evolucao.data_sessao = form.data_sessao.data
        evolucao.conteudo = form.conteudo.data  # Criptografia automática
        
        db.session.commit()
        
        flash('Evolução atualizada com sucesso!', 'success')
        return redirect(url_for('dashboard_psi.perfil_paciente', id=evolucao.paciente_id))
    
    # Pré-preencher formulário (descriptografia automática)
    form.conteudo.data = evolucao.conteudo
    
    return render_template('dashboard_psi/form_evolucao.html',
                         title='Editar Evolução',
                         form=form,
                         paciente=evolucao.paciente,
                         evolucao=evolucao)

# --- API Routes (opcional) ---
@bp.route('/api/pacientes/search')
@psicologo_required
def api_search_pacientes():
    """API para busca de pacientes (AJAX)"""
    query = request.args.get('q', '')
    
    if len(query) < 2:
        return jsonify([])
    
    pacientes = (Paciente.query
                .filter_by(psicologo_id=current_user.id)
                .filter(Paciente.nome_completo.contains(query))
                .limit(10)
                .all())
    
    results = [
        {
            'id': p.id,
            'nome': p.nome_completo,
            'idade': p.idade,
            'total_evolucoes': len(p.evolucoes)
        }
        for p in pacientes
    ]
    
    return jsonify(results)
