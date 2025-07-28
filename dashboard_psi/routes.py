# dashboard_psi/routes.py
"""
Rotas do Dashboard Psicologia adaptadas para integração
"""

from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from . import bp
from .models import Paciente, Evolucao
from .forms import PacienteForm, EvolucaoForm, PesquisaForm
from .utils import generate_id
from db import db
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func

def psicologo_required(f):
    """Decorator para verificar se o usuário é psicólogo"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Você precisa estar logado para acessar o dashboard.', 'warning')
            return redirect(url_for('p_login'))
        
        # Verificar se é psicólogo (usuário logado deve ter user_type = 'doctor')
        if not hasattr(current_user, 'user_type') or current_user.user_type != 'doctor':
            flash('Acesso restrito a psicólogos cadastrados.', 'warning')
            return redirect(url_for('p_login'))
            
        return f(*args, **kwargs)
    return decorated_function

# --- Dashboard Principal ---
@bp.route('/')
@psicologo_required
def dashboard():
    """Dashboard principal do módulo"""
    try:
        # Buscar pacientes do psicólogo atual
        pacientes = Paciente.query.filter_by(psicologo_id=current_user.id).all()
        
        # Estatísticas
        total_pacientes = len(pacientes)
        total_evolucoes = sum(len(p.evolucoes.all()) for p in pacientes)
        
        # Últimas evoluções
        ultimas_evolucoes = (Evolucao.query
                            .join(Paciente)
                            .filter(Paciente.psicologo_id == current_user.id)
                            .order_by(Evolucao.data_sessao.desc())
                            .limit(5)
                            .all())
        
        # Estatísticas por período
        hoje = datetime.now().date()
        inicio_mes = hoje.replace(day=1)
        evolucoes_mes = (Evolucao.query
                        .join(Paciente)
                        .filter(Paciente.psicologo_id == current_user.id)
                        .filter(Evolucao.data_sessao >= inicio_mes)
                        .count())
        
        return render_template('dashboard_psi/dashboard.html',
                             title='Pecci Cuidado Integrado',
                             pacientes=pacientes,
                             total_pacientes=total_pacientes,
                             total_evolucoes=total_evolucoes,
                             evolucoes_mes=evolucoes_mes,
                             ultimas_evolucoes=ultimas_evolucoes)
    except Exception as e:
        flash(f'Erro ao carregar dashboard: {str(e)}', 'error')
        return redirect(url_for('p_login'))

# --- Rotas de Pacientes ---
@bp.route('/pacientes')
@psicologo_required
def listar_pacientes():
    """Lista todos os pacientes do psicólogo"""
    try:
        form = PesquisaForm()
        search = request.args.get('search', '')
        
        query = Paciente.query.filter_by(psicologo_id=current_user.id)
        
        if search:
            query = query.filter(Paciente.nome_completo.ilike(f'%{search}%'))
        
        pacientes = query.order_by(Paciente.nome_completo).all()
        
        return render_template('dashboard_psi/listar_pacientes.html',
                             title='Pacientes',
                             pacientes=pacientes,
                             form=form,
                             search=search)
    except Exception as e:
        flash(f'Erro ao listar pacientes: {str(e)}', 'error')
        return redirect(url_for('dashboard_psi.dashboard'))

@bp.route('/pacientes/novo', methods=['GET', 'POST'])
@psicologo_required
def novo_paciente():
    """Cadastrar novo paciente"""
    form = PacienteForm()
    
    if form.validate_on_submit():
        try:
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
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar paciente: {str(e)}', 'error')
    
    return render_template('dashboard_psi/form_paciente.html',
                         title='Novo Paciente',
                         form=form)

@bp.route('/pacientes/<id>')
@psicologo_required
def perfil_paciente(id):
    """Visualizar perfil do paciente"""
    try:
        paciente = Paciente.query.filter_by(
            id=id, 
            psicologo_id=current_user.id
        ).first_or_404()
        
        # Buscar evoluções do paciente ordenadas por data
        evolucoes = Evolucao.query.filter_by(
            paciente_id=paciente.id
        ).order_by(Evolucao.data_sessao.desc()).all()
        
        return render_template('dashboard_psi/perfil_paciente.html',
                             title=f'Paciente - {paciente.nome_completo}',
                             paciente=paciente,
                             evolucoes=evolucoes)
    except Exception as e:
        flash(f'Erro ao carregar perfil do paciente: {str(e)}', 'error')
        return redirect(url_for('dashboard_psi.listar_pacientes'))

@bp.route('/pacientes/<id>/editar', methods=['GET', 'POST'])
@psicologo_required
def editar_paciente(id):
    """Editar dados do paciente"""
    try:
        paciente = Paciente.query.filter_by(
            id=id, 
            psicologo_id=current_user.id
        ).first_or_404()
        
        form = PacienteForm(obj=paciente)
        
        if form.validate_on_submit():
            form.populate_obj(paciente)
            db.session.commit()
            
            flash(f'Dados de {paciente.nome_completo} atualizados com sucesso!', 'success')
            return redirect(url_for('dashboard_psi.perfil_paciente', id=paciente.id))
        
        return render_template('dashboard_psi/form_paciente.html',
                             title=f'Editar - {paciente.nome_completo}',
                             form=form,
                             paciente=paciente)
    except Exception as e:
        flash(f'Erro ao editar paciente: {str(e)}', 'error')
        return redirect(url_for('dashboard_psi.listar_pacientes'))

# --- Rotas de Evoluções ---
@bp.route('/pacientes/<paciente_id>/evolucoes/nova', methods=['GET', 'POST'])
@psicologo_required
def nova_evolucao(paciente_id):
    """Adicionar nova evolução ao paciente"""
    try:
        paciente = Paciente.query.filter_by(
            id=paciente_id, 
            psicologo_id=current_user.id
        ).first_or_404()
        
        form = EvolucaoForm()
        
        # Preencher formulário com dados da query string se disponível
        if request.method == 'GET':
            data_param = request.args.get('data')
            tipo_param = request.args.get('tipo')
            duracao_param = request.args.get('duracao')
            conteudo_param = request.args.get('conteudo')
            
            if data_param:
                try:
                    form.data_sessao.data = datetime.strptime(data_param, '%Y-%m-%d').date()
                except ValueError:
                    pass
            
            if tipo_param:
                form.tipo_sessao.data = tipo_param
                
            if duracao_param:
                try:
                    form.duracao_minutos.data = int(duracao_param)
                except ValueError:
                    pass
                    
            if conteudo_param:
                form.conteudo.data = conteudo_param
        
        if form.validate_on_submit():
            evolucao = Evolucao(
                data_sessao=datetime.combine(form.data_sessao.data, datetime.now().time()),
                tipo_sessao=form.tipo_sessao.data,
                duracao_minutos=form.duracao_minutos.data,
                paciente_id=paciente.id
            )
            
            # Criptografar e salvar conteúdo
            evolucao.set_conteudo(form.conteudo.data)
            
            db.session.add(evolucao)
            db.session.commit()
            
            flash('Evolução adicionada com sucesso!', 'success')
            return redirect(url_for('dashboard_psi.perfil_paciente', id=paciente.id))
        
        return render_template('dashboard_psi/form_evolucao.html',
                             title=f'Nova Evolução - {paciente.nome_completo}',
                             form=form,
                             paciente=paciente)
    except Exception as e:
        flash(f'Erro ao adicionar evolução: {str(e)}', 'error')
        return redirect(url_for('dashboard_psi.listar_pacientes'))

@bp.route('/evolucoes/<id>/editar', methods=['GET', 'POST'])
@psicologo_required
def editar_evolucao(id):
    """Editar evolução existente"""
    try:
        evolucao = (Evolucao.query
                   .join(Paciente)
                   .filter(Evolucao.id == id)
                   .filter(Paciente.psicologo_id == current_user.id)
                   .first_or_404())
        
        form = EvolucaoForm()
        
        if form.validate_on_submit():
            evolucao.data_sessao = datetime.combine(form.data_sessao.data, datetime.now().time())
            evolucao.tipo_sessao = form.tipo_sessao.data
            evolucao.duracao_minutos = form.duracao_minutos.data
            evolucao.set_conteudo(form.conteudo.data)
            
            db.session.commit()
            
            flash('Evolução atualizada com sucesso!', 'success')
            return redirect(url_for('dashboard_psi.perfil_paciente', id=evolucao.paciente_id))
        
        # Preencher form com dados existentes
        form.data_sessao.data = evolucao.data_sessao.date()
        form.tipo_sessao.data = evolucao.tipo_sessao
        form.duracao_minutos.data = evolucao.duracao_minutos
        form.conteudo.data = evolucao.get_conteudo()
        
        return render_template('dashboard_psi/form_evolucao.html',
                             title='Editar Evolução',
                             form=form,
                             paciente=evolucao.paciente,
                             evolucao=evolucao)
    except Exception as e:
        flash(f'Erro ao editar evolução: {str(e)}', 'error')
        return redirect(url_for('dashboard_psi.dashboard'))

@bp.route('/evolucoes/<id>')
@psicologo_required
def ver_evolucao(id):
    """Visualizar evolução completa"""
    try:
        evolucao = (Evolucao.query
                   .join(Paciente)
                   .filter(Evolucao.id == id)
                   .filter(Paciente.psicologo_id == current_user.id)
                   .first_or_404())
        
        return render_template('dashboard_psi/ver_evolucao.html',
                             title=f'Evolução - {evolucao.paciente.nome_completo}',
                             evolucao=evolucao,
                             paciente=evolucao.paciente)
    except Exception as e:
        flash(f'Erro ao carregar evolução: {str(e)}', 'error')
        return redirect(url_for('dashboard_psi.dashboard'))

# --- API Routes ---
@bp.route('/api/estatisticas')
@psicologo_required
def api_estatisticas():
    """API para buscar estatísticas do dashboard"""
    try:
        hoje = datetime.now().date()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        inicio_mes = hoje.replace(day=1)
        
        pacientes = Paciente.query.filter_by(psicologo_id=current_user.id).all()
        
        stats = {
            'total_pacientes': len(pacientes),
            'sessoes_semana': (Evolucao.query
                              .join(Paciente)
                              .filter(Paciente.psicologo_id == current_user.id)
                              .filter(Evolucao.data_sessao >= inicio_semana)
                              .count()),
            'sessoes_mes': (Evolucao.query
                           .join(Paciente)
                           .filter(Paciente.psicologo_id == current_user.id)
                           .filter(Evolucao.data_sessao >= inicio_mes)
                           .count()),
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/pacientes/<paciente_id>/evolucoes')
@psicologo_required
def evolucoes_paciente(paciente_id):
    """Lista todas as evoluções de um paciente específico"""
    try:
        paciente = Paciente.query.filter_by(
            id=paciente_id, 
            psicologo_id=current_user.id
        ).first_or_404()
        
        # Filtros de pesquisa
        search = request.args.get('search', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        tipo_sessao = request.args.get('tipo_sessao', '')
        
        # Query base
        query = Evolucao.query.filter_by(paciente_id=paciente.id)
        
        # Aplicar filtros
        if search:
            query = query.filter(Evolucao.conteudo_criptografado.contains(search))
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(Evolucao.data_sessao >= start_dt)
            except ValueError:
                pass
                
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                query = query.filter(Evolucao.data_sessao <= end_dt)
            except ValueError:
                pass
                
        if tipo_sessao:
            query = query.filter(Evolucao.tipo_sessao == tipo_sessao)
        
        # Ordenar por data (mais recente primeiro)
        evolucoes = query.order_by(Evolucao.data_sessao.desc()).all()
        
        # Estatísticas
        stats = {
            'total_evolucoes': len(evolucoes),
            'total_horas': sum([e.duracao_minutos or 0 for e in evolucoes]) / 60,
            'primeira_sessao': evolucoes[-1].data_sessao if evolucoes else None,
            'ultima_sessao': evolucoes[0].data_sessao if evolucoes else None,
            'tipos_sessao': list(set([e.tipo_sessao for e in evolucoes if e.tipo_sessao]))
        }
        
        return render_template('dashboard_psi/evolucoes_paciente.html',
                             title=f'Evoluções - {paciente.nome_completo}',
                             paciente=paciente,
                             evolucoes=evolucoes,
                             stats=stats,
                             search=search,
                             start_date=start_date,
                             end_date=end_date,
                             tipo_sessao=tipo_sessao)
    except Exception as e:
        flash(f'Erro ao carregar evoluções: {str(e)}', 'error')
        return redirect(url_for('dashboard_psi.perfil_paciente', id=paciente_id))

# --- Rotas de Configurações ---
@bp.route('/configuracoes')
@psicologo_required
def configuracoes():
    """Página de configurações do perfil do psicólogo"""
    from .forms import PerfilForm, AlterarSenhaForm
    
    perfil_form = PerfilForm()
    senha_form = AlterarSenhaForm()
    
    # Preencher formulário com dados atuais
    perfil_form.name.data = current_user.name
    perfil_form.email.data = current_user.email
    perfil_form.crm.data = getattr(current_user, 'crm', '')
    perfil_form.telefone.data = getattr(current_user, 'phone_number', '')
    perfil_form.endereco.data = getattr(current_user, 'address', '')
    perfil_form.especialidade.data = getattr(current_user, 'specialty', '')
    perfil_form.bio.data = getattr(current_user, 'description', '')
    
    return render_template('dashboard_psi/configuracoes.html',
                         title='Configurações do Perfil',
                         perfil_form=perfil_form,
                         senha_form=senha_form)

@bp.route('/configuracoes/perfil', methods=['POST'])
@psicologo_required
def atualizar_perfil():
    """Atualizar dados do perfil do psicólogo"""
    from .forms import PerfilForm
    import os
    from werkzeug.utils import secure_filename
    from flask import current_app
    
    form = PerfilForm()
    
    if form.validate_on_submit():
        try:
            # Verificar se email já existe (exceto o próprio usuário)
            from models.doctors import Doctors
            existing_user = Doctors.query.filter(
                Doctors.email == form.email.data,
                Doctors.id != current_user.id
            ).first()
            
            if existing_user:
                flash('Este email já está sendo usado por outro usuário.', 'error')
                return redirect(url_for('dashboard_psi.configuracoes'))
            
            # Processar upload da foto se fornecida
            foto_filename = None
            if form.foto_perfil.data:
                try:
                    foto = form.foto_perfil.data
                    
                    # Criar nome do arquivo baseado no email
                    email_safe = form.email.data.replace('@', '_').replace('.', '_')
                    file_extension = os.path.splitext(secure_filename(foto.filename))[1].lower()
                    foto_filename = f"{email_safe}{file_extension}"
                    
                    # Definir pasta de uploads (usar a pasta static/uploads da aplicação principal)
                    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                    
                    # Criar pasta se não existir
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    # Caminho completo do arquivo
                    foto_path = os.path.join(upload_folder, foto_filename)
                    
                    # Remover foto anterior se existir
                    if hasattr(current_user, 'profile_picture') and current_user.profile_picture:
                        old_photo_path = os.path.join(upload_folder, current_user.profile_picture)
                        if os.path.exists(old_photo_path):
                            try:
                                os.remove(old_photo_path)
                            except:
                                pass  # Ignorar erro se não conseguir remover
                    
                    # Salvar nova foto
                    foto.save(foto_path)
                    
                except Exception as e:
                    flash(f'Erro ao fazer upload da foto: {str(e)}', 'error')
                    return redirect(url_for('dashboard_psi.configuracoes'))
            
            # Atualizar dados
            current_user.name = form.name.data
            current_user.email = form.email.data
            
            # Atualizar foto se foi feito upload
            if foto_filename and hasattr(current_user, 'profile_picture'):
                current_user.profile_picture = foto_filename
            
            # Atualizar campos opcionais se existirem no modelo
            if hasattr(current_user, 'crm'):
                current_user.crm = form.crm.data
            if hasattr(current_user, 'phone_number'):
                current_user.phone_number = form.telefone.data
            if hasattr(current_user, 'address'):
                current_user.address = form.endereco.data
            if hasattr(current_user, 'specialty'):
                current_user.specialty = form.especialidade.data
            if hasattr(current_user, 'description'):
                current_user.description = form.bio.data
            
            db.session.commit()
            flash('Perfil atualizado com sucesso!' + (' Foto alterada.' if foto_filename else ''), 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar perfil: {str(e)}', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Erro no campo {field}: {error}', 'error')
    
    return redirect(url_for('dashboard_psi.configuracoes'))

@bp.route('/configuracoes/senha', methods=['POST'])
@psicologo_required
def alterar_senha():
    """Alterar senha do psicólogo"""
    from .forms import AlterarSenhaForm
    import bcrypt
    
    form = AlterarSenhaForm()
    
    if form.validate_on_submit():
        try:
            # Verificar se o usuário tem senha definida
            if not current_user.password or current_user.password == '':
                flash('Usuário não possui senha definida. Entre em contato com o administrador.', 'error')
                return redirect(url_for('dashboard_psi.configuracoes'))
            
            # Verificar senha atual usando bcrypt
            try:
                if not bcrypt.checkpw(form.senha_atual.data.encode('utf-8'), current_user.password.encode('utf-8')):
                    flash('Senha atual incorreta.', 'error')
                    return redirect(url_for('dashboard_psi.configuracoes'))
            except (ValueError, TypeError) as e:
                flash('Erro na verificação da senha atual. Entre em contato com o administrador.', 'error')
                return redirect(url_for('dashboard_psi.configuracoes'))
            
            # Verificar se a nova senha é diferente da atual
            try:
                if bcrypt.checkpw(form.nova_senha.data.encode('utf-8'), current_user.password.encode('utf-8')):
                    flash('A nova senha deve ser diferente da senha atual.', 'error')
                    return redirect(url_for('dashboard_psi.configuracoes'))
            except (ValueError, TypeError):
                # Se não conseguir verificar, assumir que a senha é diferente
                pass
            
            # Atualizar senha usando bcrypt
            hashed_password = bcrypt.hashpw(form.nova_senha.data.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            current_user.password = hashed_password
            db.session.commit()
            
            flash('Senha alterada com sucesso!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao alterar senha: {str(e)}', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Erro no campo {field}: {error}', 'error')
    
    return redirect(url_for('dashboard_psi.configuracoes'))

# --- Rotas de Agenda ---
@bp.route('/agenda')
@psicologo_required
def agenda():
    """Página principal da agenda"""
    from .forms import FiltroAgendaForm
    from .models import Agenda, Paciente
    from datetime import datetime, timedelta
    
    form = FiltroAgendaForm()
    
    # Configurar choices do paciente
    pacientes = Paciente.query.filter_by(psicologo_id=current_user.id).all()
    form.paciente_id.choices = [('', 'Todos os pacientes')] + [(str(p.id), p.nome_completo) for p in pacientes]
    
    # Data padrão - mostrar próximos 30 dias
    today = datetime.now().date()
    default_end = today + timedelta(days=30)
    
    # Filtros
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    paciente_id = request.args.get('paciente_id')
    status = request.args.get('status')
    
    # Query base
    query = Agenda.query.filter_by(psicologo_id=current_user.id)
    
    # Aplicar filtros
    if data_inicio:
        try:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Agenda.data_hora) >= data_inicio)
        except ValueError:
            data_inicio = today
    else:
        data_inicio = today
        query = query.filter(db.func.date(Agenda.data_hora) >= data_inicio)
    
    if data_fim:
        try:
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Agenda.data_hora) <= data_fim)
        except ValueError:
            data_fim = default_end
    else:
        data_fim = default_end
        query = query.filter(db.func.date(Agenda.data_hora) <= data_fim)
    
    if paciente_id:
        query = query.filter_by(paciente_id=paciente_id)
    
    if status:
        query = query.filter_by(status=status)
    
    # Ordenar por data
    agendamentos = query.order_by(Agenda.data_hora).all()
    
    # Estatísticas
    stats = {
        'total': len(agendamentos),
        'hoje': sum(1 for a in agendamentos if a.data_hora.date() == today),
        'semana': sum(1 for a in agendamentos if a.data_hora.date() <= today + timedelta(days=7)),
        'agendadas': sum(1 for a in agendamentos if a.status == 'agendada'),
        'confirmadas': sum(1 for a in agendamentos if a.status == 'confirmada'),
    }
    
    # Preencher form com valores dos filtros
    form.data_inicio.data = data_inicio
    form.data_fim.data = data_fim
    if paciente_id:
        form.paciente_id.data = paciente_id
    if status:
        form.status.data = status
    
    return render_template('dashboard_psi/agenda.html',
                         title='Agenda',
                         agendamentos=agendamentos,
                         form=form,
                         stats=stats)

@bp.route('/agenda/novo', methods=['GET', 'POST'])
@psicologo_required
def novo_agendamento():
    """Criar novo agendamento"""
    from .forms import AgendaForm
    from .models import Agenda, Paciente
    from .utils import criar_agendamentos_recorrentes
    from datetime import datetime
    
    form = AgendaForm()
    
    # Configurar choices do paciente
    pacientes = Paciente.query.filter_by(psicologo_id=current_user.id).all()
    form.paciente_id.choices = [(str(p.id), p.nome_completo) for p in pacientes]
    
    if form.validate_on_submit():
        try:
            # Combinar data e hora
            data_hora = datetime.combine(form.data_consulta.data, form.hora_consulta.data)
            
            # Verificar se já existe agendamento no mesmo horário
            conflito = Agenda.query.filter(
                Agenda.psicologo_id == current_user.id,
                Agenda.data_hora == data_hora,
                Agenda.status.in_(['agendada', 'confirmada'])
            ).first()
            
            if conflito:
                flash('Já existe um agendamento confirmado neste horário.', 'error')
                return render_template('dashboard_psi/form_agendamento.html',
                                     title='Novo Agendamento',
                                     form=form)
            
            # Verificar se é um agendamento recorrente
            if form.recorrente.data:
                # Criar série de agendamentos recorrentes
                try:
                    agendamentos_criados = criar_agendamentos_recorrentes(
                        paciente_id=form.paciente_id.data,
                        psicologo_id=current_user.id,
                        data_hora_inicial=data_hora,
                        compromissos=form.compromissos.data,
                        local=form.local.data,
                        observacoes=form.observacoes.data,
                        status=form.status.data,
                        recorrencia_tipo=form.recorrencia_tipo.data,
                        recorrencia_periodo=form.recorrencia_periodo.data
                    )
                    
                    total_agendamentos = len(agendamentos_criados)
                    if total_agendamentos > 1:
                        flash(f'Série de {total_agendamentos} agendamentos recorrentes criada com sucesso!', 'success')
                    else:
                        flash('Agendamento criado com sucesso!', 'success')
                    
                except Exception as e:
                    db.session.rollback()
                    flash(f'Erro ao criar agendamentos recorrentes: {str(e)}', 'error')
                    return render_template('dashboard_psi/form_agendamento.html',
                                         title='Novo Agendamento',
                                         form=form)
            else:
                # Criar agendamento único
                agendamento = Agenda(
                    paciente_id=form.paciente_id.data,
                    psicologo_id=current_user.id,
                    data_hora=data_hora,
                    compromissos=form.compromissos.data,
                    local=form.local.data,
                    observacoes=form.observacoes.data,
                    status=form.status.data,
                    recorrente=False
                )
                
                db.session.add(agendamento)
                db.session.commit()
                flash('Agendamento criado com sucesso!', 'success')
            
            return redirect(url_for('dashboard_psi.agenda'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar agendamento: {str(e)}', 'error')
    
    return render_template('dashboard_psi/form_agendamento.html',
                         title='Novo Agendamento',
                         form=form)

@bp.route('/agenda/<agendamento_id>')
@psicologo_required
def ver_agendamento(agendamento_id):
    """Ver detalhes do agendamento"""
    from .models import Agenda
    
    agendamento = Agenda.query.filter_by(
        id=agendamento_id,
        psicologo_id=current_user.id
    ).first_or_404()
    
    return render_template('dashboard_psi/ver_agendamento.html',
                         title=f'Agendamento - {agendamento.paciente.nome_completo}',
                         agendamento=agendamento)

@bp.route('/agenda/<agendamento_id>/editar', methods=['GET', 'POST'])
@psicologo_required
def editar_agendamento(agendamento_id):
    """Editar agendamento"""
    from .forms import AgendaForm
    from .models import Agenda, Paciente
    from datetime import datetime
    
    agendamento = Agenda.query.filter_by(
        id=agendamento_id,
        psicologo_id=current_user.id
    ).first_or_404()
    
    form = AgendaForm(obj=agendamento)
    
    # Configurar choices do paciente
    pacientes = Paciente.query.filter_by(psicologo_id=current_user.id).all()
    form.paciente_id.choices = [(str(p.id), p.nome_completo) for p in pacientes]
    
    # Preencher dados do agendamento
    form.paciente_id.data = str(agendamento.paciente_id)
    form.data_consulta.data = agendamento.data_hora.date()
    form.hora_consulta.data = agendamento.data_hora.time()
    
    if form.validate_on_submit():
        try:
            # Combinar data e hora
            nova_data_hora = datetime.combine(form.data_consulta.data, form.hora_consulta.data)
            
            # Verificar conflitos (exceto o próprio agendamento)
            if nova_data_hora != agendamento.data_hora:
                conflito = Agenda.query.filter(
                    Agenda.psicologo_id == current_user.id,
                    Agenda.data_hora == nova_data_hora,
                    Agenda.status.in_(['agendada', 'confirmada']),
                    Agenda.id != agendamento.id
                ).first()
                
                if conflito:
                    flash('Já existe um agendamento confirmado neste horário.', 'error')
                    return render_template('dashboard_psi/form_agendamento.html',
                                         title='Editar Agendamento',
                                         form=form,
                                         agendamento=agendamento)
            
            # Atualizar dados
            agendamento.paciente_id = form.paciente_id.data
            agendamento.data_hora = nova_data_hora
            agendamento.compromissos = form.compromissos.data
            agendamento.local = form.local.data
            agendamento.observacoes = form.observacoes.data
            agendamento.status = form.status.data
            
            db.session.commit()
            
            flash('Agendamento atualizado com sucesso!', 'success')
            return redirect(url_for('dashboard_psi.ver_agendamento', agendamento_id=agendamento.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar agendamento: {str(e)}', 'error')
    
    return render_template('dashboard_psi/form_agendamento.html',
                         title='Editar Agendamento',
                         form=form,
                         agendamento=agendamento)

@bp.route('/agenda/<agendamento_id>/deletar', methods=['POST'])
@psicologo_required
def deletar_agendamento(agendamento_id):
    """Deletar agendamento"""
    from .models import Agenda
    
    agendamento = Agenda.query.filter_by(
        id=agendamento_id,
        psicologo_id=current_user.id
    ).first_or_404()
    
    try:
        db.session.delete(agendamento)
        db.session.commit()
        flash('Agendamento removido com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover agendamento: {str(e)}', 'error')
    
    return redirect(url_for('dashboard_psi.agenda'))

@bp.route('/agenda/<agendamento_id>/status', methods=['POST'])
@psicologo_required
def alterar_status_agendamento(agendamento_id):
    """Alterar status do agendamento via AJAX"""
    from .models import Agenda
    
    agendamento = Agenda.query.filter_by(
        id=agendamento_id,
        psicologo_id=current_user.id
    ).first_or_404()
    
    novo_status = request.json.get('status')
    
    if novo_status not in ['agendada', 'confirmada', 'cancelada', 'concluida']:
        return {'success': False, 'message': 'Status inválido'}, 400
    
    try:
        agendamento.status = novo_status
        db.session.commit()
        return {'success': True, 'message': 'Status atualizado com sucesso'}
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': str(e)}, 500

@bp.route('/agenda/preview-recorrencia', methods=['POST'])
@psicologo_required
def preview_recorrencia():
    """Preview dos agendamentos recorrentes via AJAX"""
    from .utils import calcular_agendamentos_recorrentes
    from datetime import datetime
    import json
    
    try:
        data = request.get_json()
        
        # Validar dados recebidos
        if not data or not all(k in data for k in ['data', 'hora', 'tipo', 'periodo']):
            return {'success': False, 'message': 'Dados incompletos'}, 400
        
        # Converter data e hora
        data_str = data['data']
        hora_str = data['hora']
        
        try:
            data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
            hora_obj = datetime.strptime(hora_str, '%H:%M').time()
            data_hora = datetime.combine(data_obj, hora_obj)
        except ValueError:
            return {'success': False, 'message': 'Formato de data/hora inválido'}, 400
        
        # Calcular as datas dos agendamentos
        datas = calcular_agendamentos_recorrentes(
            data_hora_inicial=data_hora,
            recorrencia_tipo=data['tipo'],
            recorrencia_periodo=int(data['periodo'])
        )
        
        # Formatar as datas para retorno
        datas_formatadas = []
        for data_agendamento in datas:
            datas_formatadas.append({
                'data': data_agendamento.strftime('%d/%m/%Y'),
                'hora': data_agendamento.strftime('%H:%M'),
                'data_completa': data_agendamento.strftime('%d/%m/%Y às %H:%M')
            })
        
        return {
            'success': True,
            'total': len(datas_formatadas),
            'agendamentos': datas_formatadas
        }
        
    except Exception as e:
        return {'success': False, 'message': f'Erro interno: {str(e)}'}, 500

@bp.route('/agenda/recorrencia/<grupo_id>/deletar', methods=['POST'])
@psicologo_required
def deletar_recorrencia(grupo_id):
    """Deletar todos os agendamentos de uma recorrência"""
    from .models import Agenda
    
    try:
        # Buscar todos os agendamentos do grupo de recorrência
        agendamentos = Agenda.query.filter(
            Agenda.recorrencia_grupo_id == grupo_id,
            Agenda.psicologo_id == current_user.id
        ).all()
        
        if not agendamentos:
            flash('Nenhum agendamento encontrado nesta recorrência.', 'warning')
            return redirect(url_for('dashboard_psi.agenda'))
        
        # Contar quantos serão deletados
        total = len(agendamentos)
        
        # Deletar todos os agendamentos do grupo
        for agendamento in agendamentos:
            db.session.delete(agendamento)
        
        db.session.commit()
        flash(f'{total} agendamento(s) da recorrência foram deletados com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao deletar recorrência: {str(e)}', 'error')
    
    return redirect(url_for('dashboard_psi.agenda'))

# --- Rotas de Exportação PDF ---
@bp.route('/evolucoes/<id>/pdf')
@psicologo_required
def exportar_evolucao_pdf(id):
    """Exportar evolução específica para PDF"""
    try:
        # Buscar evolução
        evolucao = (Evolucao.query
                   .join(Paciente)
                   .filter(Evolucao.id == id)
                   .filter(Paciente.psicologo_id == current_user.id)
                   .first_or_404())
        
        # Importar PDF generator
        from .pdf_utils import pdf_generator
        
        # Gerar PDF
        pdf_buffer = pdf_generator.gerar_pdf_evolucao(
            evolucao=evolucao,
            paciente=evolucao.paciente,
            psicologo=current_user
        )
        
        # Preparar resposta
        from flask import Response
        
        # Nome do arquivo
        data_formatada = evolucao.data_sessao.strftime('%Y%m%d')
        paciente_nome = evolucao.paciente.nome_completo.replace(' ', '_')
        filename = f"Evolucao_{paciente_nome}_{data_formatada}.pdf"
        
        return Response(
            pdf_buffer.getvalue(),
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'application/pdf'
            }
        )
        
    except Exception as e:
        flash(f'Erro ao gerar PDF da evolução: {str(e)}', 'error')
        return redirect(url_for('dashboard_psi.ver_evolucao', id=id))

@bp.route('/pacientes/<id>/pdf-completo')
@psicologo_required
def exportar_paciente_completo_pdf(id):
    """Exportar prontuário completo do paciente para PDF"""
    try:
        # Buscar paciente
        paciente = Paciente.query.filter_by(
            id=id, 
            psicologo_id=current_user.id
        ).first_or_404()
        
        # Buscar todas as evoluções do paciente
        evolucoes = Evolucao.query.filter_by(
            paciente_id=paciente.id
        ).order_by(Evolucao.data_sessao.asc()).all()
        
        # Importar PDF generator
        from .pdf_utils import pdf_generator
        
        # Gerar PDF
        pdf_buffer = pdf_generator.gerar_pdf_paciente_completo(
            paciente=paciente,
            evolucoes=evolucoes,
            psicologo=current_user
        )
        
        # Preparar resposta
        from flask import Response
        
        # Nome do arquivo
        paciente_nome = paciente.nome_completo.replace(' ', '_')
        data_atual = datetime.now().strftime('%Y%m%d')
        filename = f"Prontuario_Completo_{paciente_nome}_{data_atual}.pdf"
        
        return Response(
            pdf_buffer.getvalue(),
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'application/pdf'
            }
        )
        
    except Exception as e:
        flash(f'Erro ao gerar PDF completo do paciente: {str(e)}', 'error')
        return redirect(url_for('dashboard_psi.perfil_paciente', id=id))
