from flask import Flask, render_template, redirect, request, flash, session, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from db import db, migrate
from flask_sitemap import Sitemap
# Controllers
from controllers.doctors_controller import DoctorsController
from controllers.user_controller import UserController
from controllers.appointments_controller import AppointmentsController
from controllers.slot_controller import SlotsController
from controllers.blog_controller import BlogController


# Importar todos os modelos para que o SQLAlchemy os reconheça
from models.user import User
from models.doctors import Doctors
from models.appointments import Appointments
from models.blog_model import BlogModel
from dashboard_psi.models import Paciente, Evolucao
import config
from models.slots import Slots


import bcrypt
from decimal import Decimal, ROUND_HALF_UP

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)
migrate.init_app(app, db)
sitemap = Sitemap(app=app)
app.config['SERVER_NAME'] = 'peccicuidadointegrado.com.br'
app.config["SITEMAP_URL_SCHEME"] = "https" 
# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'p_login'  # Mudado para login de psicólogo
login_manager.login_message = 'Você precisa estar logado como psicólogo para acessar esta página'
login_manager.login_message_category = 'error'

@login_manager.user_loader
def load_user(user_id):
    # Carregar apenas doutores (usuários comuns não fazem mais login)
    doctor = Doctors.query.get(user_id)
    if doctor:
        doctor.user_type = 'doctor'
        return doctor
    
    return None
if app.config['DEBUG'] == True:
    print("Debug mode is ON")
    print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])
    print("App Name:", app.config['APP_NAME'])
    print("App Version:", app.config['APP_VERSION'])
    print("Upload Folder:", app.config['UPLOAD_FOLDER'])
    print("Allowed Extensions:", app.config['ALLOWED_EXTENSIONS'])
    print("Session Cookie Name:", app.config['SESSION_COOKIE_NAME'])
    print("Secret Key:", app.config['APP_SECRET_KEY'])

@app.route('/', methods=['GET'])
def index():
    doctors = DoctorsController().get_all_doctors()
    
    # Buscar os últimos 3 posts do blog para a seção de notícias
    blog_controller = BlogController()
    recent_blog_posts = blog_controller.get_recent_posts(3)
    
    return render_template('index.html', doctors=doctors, recent_blog_posts=recent_blog_posts)

# Rotas removidas: /register, /login (para usuários comuns)
# Agora apenas psicólogos fazem login através de /p/login

@app.route('/create_doctor', methods=['GET', 'POST'])
def create_doctor():
    """Rota redirecionada para acesso administrativo"""
    flash('O cadastro de psicólogos agora requer acesso administrativo.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/doctors', methods=['GET', 'POST'])
def doctors():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        specialty = request.form['specialty']
        
        try:
            doctors_controller = DoctorsController()
            new_doctor = doctors_controller.create_doctor(email, name, password, specialty)
            flash(f'Doutor {new_doctor.name} criado com sucesso!', 'success')
            return redirect('/doctors')
        
        except Exception as e:
            flash(f'Erro ao criar doutor: {str(e)}', 'error')
    
    doctors = DoctorsController().get_all_doctors()
    return render_template('doctors.html', doctors=doctors)

@app.route('/psychologist_dashboard')
@login_required
def psychologist_dashboard():
    # Redirecionar para o novo dashboard
    return redirect(url_for('dashboard_psi.dashboard'))

@app.route('/p/login', methods=['GET', 'POST'])
def p_login():
    # Se já estiver logado como psicólogo, redirecionar
    if current_user.is_authenticated and hasattr(current_user, 'user_type') and current_user.user_type == 'doctor':
        # Verificar se há um parâmetro de redirecionamento
        next_page = request.args.get('next')
        if next_page:
            # Verificar se é uma URL segura (dentro do domínio)
            if next_page.startswith('/'):
                return redirect(next_page)
        return redirect(url_for('dashboard_psi.dashboard'))
    
    if request.method == 'POST':
        # Suporte tanto para formulário normal quanto AJAX
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            remember = data.get('remember', False)
        else:
            email = request.form['email']
            password = request.form['password']
            remember = request.form.get('remember', False)
        
        try:
            # Buscar psicólogo no banco de dados
            doctors_controller = DoctorsController()
            doctor = db.session.query(Doctors).filter_by(email=email).first()
            
            if doctor and bcrypt.checkpw(password.encode('utf-8'), doctor.password.encode('utf-8')):
                # Login de psicólogo bem-sucedido
                doctor.user_type = 'doctor'
                login_user(doctor, remember=remember)
                
                # Verificar redirecionamento
                next_page = request.args.get('next') or request.form.get('next')
                
                if request.is_json:
                    redirect_url = next_page if next_page and next_page.startswith('/') else url_for('dashboard_psi.dashboard')
                    return jsonify({
                        'success': True, 
                        'message': f'Bem-vindo ao dashboard, Dr(a). {doctor.name}!',
                        'redirect_url': redirect_url
                    })
                else:
                    flash(f'Bem-vindo ao dashboard, Dr(a). {doctor.name}!', 'success')
                    if next_page and next_page.startswith('/'):
                        return redirect(next_page)
                    return redirect(url_for('dashboard_psi.dashboard'))
            else:
                if request.is_json:
                    return jsonify({
                        'success': False, 
                        'message': 'Email ou senha inválidos para psicólogo'
                    }), 401
                else:
                    flash('Email ou senha inválidos para psicólogo', 'error')
                
        except Exception as e:
            if request.is_json:
                return jsonify({
                    'success': False, 
                    'message': f'Erro no login do psicólogo: {str(e)}'
                }), 500
            else:
                flash(f'Erro no login do psicólogo: {str(e)}', 'error')
    
    return render_template('psychologist_login.html')

@app.route('/create_schedule', methods=['POST'])
@login_required
def create_schedule():
    # Verificar se o usuário logado é um psicólogo
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'doctor':
        flash('Você precisa estar logado como psicólogo para cadastrar horários', 'error')
        return redirect('/p/login')
    
    try:
        doctor_id = current_user.id
        schedule_date = request.form.get('schedule_date')
        schedule_type = request.form.get('schedule_type')
        time_slots = request.form.getlist('time_slots[]')
        duration = int(request.form.get('duration', 50))
        price = request.form.get('price')
        notes = request.form.get('notes', '')
        recurring = request.form.get('recurring') == 'on'
        recurring_weeks = int(request.form.get('recurring_weeks', 1)) if recurring else 1
        
        # Preco para centavos
        if price:
            preco_decimal = Decimal(str(price))
            centavos = (preco_decimal * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            price = int(centavos)

        # Validações
        if not schedule_date or not schedule_type or not time_slots:
            flash('Por favor, preencha todos os campos obrigatórios', 'error')
            return redirect(url_for('dashboard_psi.dashboard'))
        
        slots_controller = SlotsController()
        created_slots = 0
        
        # Criar horários para cada semana se for recorrente
        from datetime import datetime, timedelta
        base_date = datetime.strptime(schedule_date, '%Y-%m-%d').date()
        
        for week in range(recurring_weeks):
            current_date = base_date + timedelta(weeks=week)
            
            # Criar horário para cada time slot selecionado
            for time_slot in time_slots:
                start_time = datetime.strptime(time_slot, '%H:%M').time()
                
                # Calcular end_time baseado na duração
                start_datetime = datetime.combine(current_date, start_time)
                end_datetime = start_datetime + timedelta(minutes=duration)
                end_time = end_datetime.time()
                
                # Verificar se já existe um horário no mesmo período
                existing_slot = slots_controller.get_slot_by_doctor_date_time(
                    doctor_id, current_date, start_time
                )
                
                if not existing_slot:
                    new_slot = slots_controller.create_slot(
                        doctor_id=doctor_id,
                        appointment_date=current_date,
                        start_time=start_time,
                        end_time=end_time,
                        appointment_type=schedule_type,
                        price=int(price) if price else None,
                        notes=notes
                    )
                    created_slots += 1
        
        if created_slots > 0:
            flash(f'{created_slots} horário(s) cadastrado(s) com sucesso!', 'success')
        else:
            flash('Nenhum horário novo foi cadastrado. Verifique se já existem horários nos períodos selecionados.', 'warning')
            
    except Exception as e:
        flash(f'Erro ao cadastrar horários: {str(e)}', 'error')
    
    return redirect(url_for('dashboard_psi.dashboard'))

@app.route('/create_appointment', methods=['POST'])
@login_required
def create_appointment():
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'doctor':
        flash('Você precisa estar logado como psicólogo para agendar consultas', 'error')
        return redirect('/p/login')
    
    try:
        # Coletar dados do formulário
        patient_id = request.form.get('patient_id')
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')
        appointment_type = request.form.get('appointment_type')
        appointment_duration = request.form.get('appointment_duration', '50')
        appointment_price = request.form.get('appointment_price')
        appointment_notes = request.form.get('appointment_notes', '')
        send_confirmation = request.form.get('send_confirmation') == 'on'
        send_reminder = request.form.get('send_reminder') == 'on'
        recurring_appointment = request.form.get('recurring_appointment') == 'on'
        recurrence_frequency = request.form.get('recurrence_frequency', 'weekly')
        recurrence_count = request.form.get('recurrence_count', '1')
        
        doctor_id = current_user.id
        
        # Validar dados obrigatórios
        if not all([patient_id, appointment_date, appointment_time, appointment_type]):
            flash('Por favor, preencha todos os campos obrigatórios', 'error')
            return redirect(url_for('dashboard_psi.dashboard'))
        
        # Verificar se o paciente existe
        userController = UserController()
        patient = userController.get_user_by_id(patient_id)
        if not patient:
            flash('Paciente não encontrado', 'error')
            return redirect(url_for('dashboard_psi.dashboard'))
        
        # Verificar se o horário está disponível
        slController = SlotsController()
        # Aqui seria verificado se o slot está realmente disponível
        
        # Criar a consulta
        appointmentsController = AppointmentsController()
        
        # Converter dados para formato adequado
        import datetime
        appointment_datetime = datetime.datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
        
        # Criar consulta principal
        new_appointment = appointmentsController.create_appointment(
            user_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            appointment_type=appointment_type,
            notes=appointment_notes,
            price=float(appointment_price) if appointment_price else None,
            duration=int(appointment_duration)
        )
        
        if new_appointment:
            # Incrementar contador de consultas do paciente
            userController.increment_appointment_count(patient_id)
            
            appointments_created = 1
            
            # Se for consulta recorrente, criar as próximas
            if recurring_appointment and recurrence_count:
                try:
                    recurrence_count = int(recurrence_count)
                    base_date = datetime.datetime.strptime(appointment_date, "%Y-%m-%d")
                    
                    for i in range(1, recurrence_count):
                        if recurrence_frequency == 'weekly':
                            next_date = base_date + datetime.timedelta(weeks=i)
                        elif recurrence_frequency == 'biweekly':
                            next_date = base_date + datetime.timedelta(weeks=i*2)
                        elif recurrence_frequency == 'monthly':
                            # Aproximação para mensal (30 dias)
                            next_date = base_date + datetime.timedelta(days=i*30)
                        
                        next_appointment = appointmentsController.create_appointment(
                            user_id=patient_id,
                            doctor_id=doctor_id,
                            appointment_date=next_date.strftime("%Y-%m-%d"),
                            appointment_time=appointment_time,
                            appointment_type=appointment_type,
                            notes=f"{appointment_notes} (Consulta recorrente {i+1}/{recurrence_count})",
                            price=float(appointment_price) if appointment_price else None,
                            duration=int(appointment_duration)
                        )
                        
                        if next_appointment:
                            appointments_created += 1
                            userController.increment_appointment_count(patient_id)
                
                except Exception as e:
                    flash(f'Consulta principal criada, mas houve erro ao criar consultas recorrentes: {str(e)}', 'warning')
            
            # Mensagem de sucesso
            if appointments_created == 1:
                flash(f'Consulta agendada com sucesso para {patient.name}!', 'success')
            else:
                flash(f'{appointments_created} consultas agendadas com sucesso para {patient.name}!', 'success')
            
            # Aqui você poderia adicionar lógica para:
            # - Enviar email de confirmação se send_confirmation for True
            # - Configurar lembrete se send_reminder for True
            # - Marcar o slot como ocupado
            
        else:
            flash('Erro ao criar a consulta. Tente novamente.', 'error')
            
    except Exception as e:
        flash(f'Erro ao agendar consulta: {str(e)}', 'error')
    
    return redirect(url_for('dashboard_psi.dashboard'))

@app.route('/get_available_times', methods=['POST'])
@login_required
def get_available_times():
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'doctor':
        return jsonify({'error': 'Não autenticado'}), 401
    
    try:
        data = request.get_json()
        selected_date = data.get('date')
        doctor_id = current_user.id
        
        if not selected_date:
            return jsonify({'error': 'Data não fornecida'}), 400
        
        # Buscar slots disponíveis para a data
        slController = SlotsController()
        available_slots = slController.get_available_slots_by_date(doctor_id, selected_date)
        
        # Se não houver slots específicos, retornar horários padrão
        if not available_slots:
            default_times = [
                {'value': '08:00', 'text': '08:00 - Disponível'},
                {'value': '09:00', 'text': '09:00 - Disponível'},
                {'value': '10:00', 'text': '10:00 - Disponível'},
                {'value': '14:00', 'text': '14:00 - Disponível'},
                {'value': '15:00', 'text': '15:00 - Disponível'},
                {'value': '16:00', 'text': '16:00 - Disponível'},
            ]
            return jsonify({'times': default_times})
        
        # Formatar slots para o select
        times = []
        for slot in available_slots:
            times.append({
                'value': slot.start_time.strftime('%H:%M'),
                'text': f"{slot.start_time.strftime('%H:%M')} - Disponível"
            })
        
        return jsonify({'times': times})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_patient_info', methods=['POST'])
@login_required
def get_patient_info():
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'doctor':
        return jsonify({'error': 'Não autenticado'}), 401
    
    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        
        if not patient_id:
            return jsonify({'error': 'ID do paciente não fornecido'}), 400
        
        # Buscar informações do paciente
        userController = UserController()
        patient = userController.get_user_by_id(patient_id)
        
        if not patient:
            return jsonify({'error': 'Paciente não encontrado'}), 404
        
        # Buscar número de consultas
        appointmentsController = AppointmentsController()
        appointments = appointmentsController.get_appointments_by_user(patient_id)
        appointment_count = len(appointments) if appointments else 0
        
        return jsonify({
            'name': patient.name,
            'email': patient.email,
            'phone': patient.phone_number or 'Não informado',
            'appointment_count': appointment_count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/blog', methods=['GET'])
def blog():
    blog_controller = BlogController()
    posts = blog_controller.get_all_posts()
    
    # Buscar posts recentes para a sidebar (últimos 5)
    recent_posts = posts[-5:] if posts else []
    
    # Verificar se é um doutor logado
    is_doctor = current_user.is_authenticated and hasattr(current_user, 'user_type') and current_user.user_type == 'doctor'
    doctor_name = current_user.name if is_doctor else None

    return render_template('blog.html', posts=posts, recent_posts=recent_posts, is_doctor=is_doctor, doctor_name=doctor_name)

@app.route('/blog/create', methods=['GET', 'POST'])
@login_required
def create_blog_post():
    # Verificar se é um doutor logado
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'doctor':
        flash('Apenas psicólogos podem criar posts no blog', 'error')
        return redirect('/blog')
    
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            image_file = request.files.get('image_file', None)
            image_url = None
            
            if not title or not content:
                flash('Título e conteúdo são obrigatórios', 'error')
                return render_template('create_blog_post.html')
            
            # Processar upload da imagem se fornecida
            if image_file and image_file.filename:
                # Validar extensão do arquivo
                allowed_extensions = app.config['ALLOWED_EXTENSIONS']
                if not any(image_file.filename.lower().endswith(ext) for ext in allowed_extensions):
                    flash('Formato de imagem inválido. Use JPG, PNG ou GIF.', 'error')
                    return render_template('create_blog_post.html')
                
                # Verificar tamanho do arquivo (5MB máximo)
                if len(image_file.read()) > 5 * 1024 * 1024:
                    flash('A imagem deve ter no máximo 5MB.', 'error')
                    return render_template('create_blog_post.html')
                
                # Resetar o ponteiro do arquivo após verificar o tamanho
                image_file.seek(0)
                
                # Criar nome único para o arquivo
                import uuid
                import os
                file_extension = os.path.splitext(image_file.filename)[1]
                unique_filename = f"blog_post_{uuid.uuid4().hex}{file_extension}"
                
                # Criar diretório se não existir
                blog_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'blog_posts')
                os.makedirs(blog_upload_dir, exist_ok=True)
                
                # Salvar arquivo
                image_path = os.path.join(blog_upload_dir, unique_filename)
                image_file.save(image_path)
                
                # Salvar caminho relativo para o banco de dados
                image_url = f"/static/uploads/blog_posts/{unique_filename}"
            
            blog_controller = BlogController()
            new_post = blog_controller.create_post(
                title=title,
                content=content,
                author_id=current_user.id,
                image_url=image_url
            )
            
            flash('Post criado com sucesso!', 'success')
            return redirect('/blog')
            
        except Exception as e:
            flash(f'Erro ao criar post: {str(e)}', 'error')
    
    return render_template('create_blog_post.html')

@app.route('/blog/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_blog_post(post_id):
    # Verificar se é um doutor logado
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'doctor':
        flash('Apenas psicólogos podem editar posts', 'error')
        return redirect('/blog')
    
    blog_controller = BlogController()
    post = blog_controller.get_post_by_id(post_id)
    
    if not post:
        flash('Post não encontrado', 'error')
        return redirect('/blog')
    
    # Verificar se o doutor é o autor do post
    if post.author_id != current_user.id:
        flash('Você só pode editar seus próprios posts', 'error')
        return redirect('/blog')
    
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            image_file = request.files.get('image_file', None)
            image_url = post.image_url  # Manter imagem atual por padrão
            
            if not title or not content:
                flash('Título e conteúdo são obrigatórios', 'error')
                return render_template('edit_blog_post.html', post=post)
            
            # Processar upload da nova imagem se fornecida
            if image_file and image_file.filename:
                # Validar extensão do arquivo
                allowed_extensions = app.config['ALLOWED_EXTENSIONS']
                if not any(image_file.filename.lower().endswith(ext) for ext in allowed_extensions):
                    flash('Formato de imagem inválido. Use JPG, PNG ou GIF.', 'error')
                    return render_template('edit_blog_post.html', post=post)
                
                # Verificar tamanho do arquivo (5MB máximo)
                if len(image_file.read()) > 5 * 1024 * 1024:
                    flash('A imagem deve ter no máximo 5MB.', 'error')
                    return render_template('edit_blog_post.html', post=post)
                
                # Resetar o ponteiro do arquivo após verificar o tamanho
                image_file.seek(0)
                
                # Remover imagem antiga se existir
                if post.image_url:
                    import os
                    old_image_path = os.path.join(app.root_path, 'static', post.image_url.lstrip('/static/'))
                    if os.path.exists(old_image_path):
                        try:
                            os.remove(old_image_path)
                        except:
                            pass  # Ignorar erro se não conseguir remover
                
                # Criar nome único para o arquivo
                import uuid
                import os
                file_extension = os.path.splitext(image_file.filename)[1]
                unique_filename = f"blog_post_{uuid.uuid4().hex}{file_extension}"
                
                # Criar diretório se não existir
                blog_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'blog_posts')
                os.makedirs(blog_upload_dir, exist_ok=True)
                
                # Salvar arquivo
                image_path = os.path.join(blog_upload_dir, unique_filename)
                image_file.save(image_path)
                
                # Salvar caminho relativo para o banco de dados
                image_url = f"/static/uploads/blog_posts/{unique_filename}"
            
            updated_post = blog_controller.update_post(
                post_id=post_id,
                title=title,
                content=content,
                image_url=image_url
            )
            
            if updated_post:
                flash('Post atualizado com sucesso!', 'success')
                return redirect('/blog')
            else:
                flash('Erro ao atualizar post', 'error')
            
        except Exception as e:
            flash(f'Erro ao atualizar post: {str(e)}', 'error')
    
    return render_template('edit_blog_post.html', post=post)

@app.route('/blog/post/<int:post_id>', methods=['GET'])
def view_blog_post(post_id):
    blog_controller = BlogController()
    post = blog_controller.get_post_by_id(post_id)
    
    if not post:
        flash('Post não encontrado', 'error')
        return redirect('/blog')
    
    # Buscar posts recentes para a sidebar (últimos 5, excluindo o atual)
    all_posts = blog_controller.get_all_posts()
    recent_posts = [p for p in all_posts[-5:] if p.id != post_id]
    
    # Verificar se é um doutor logado
    is_doctor = current_user.is_authenticated and hasattr(current_user, 'user_type') and current_user.user_type == 'doctor'
    
    return render_template('view_blog_post.html', post=post, recent_posts=recent_posts, is_doctor=is_doctor)

@app.route('/blog/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_blog_post(post_id):
    # Verificar se é um doutor logado
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'doctor':
        flash('Apenas psicólogos podem excluir posts', 'error')
        return redirect('/blog')
    
    try:
        blog_controller = BlogController()
        post = blog_controller.get_post_by_id(post_id)
        
        if not post:
            flash('Post não encontrado', 'error')
            return redirect('/blog')
        
        # Verificar se o doutor é o autor do post
        if post.author_id != current_user.id:
            flash('Você só pode excluir seus próprios posts', 'error')
            return redirect('/blog')
        
        deleted_post = blog_controller.delete_post(post_id)
        
        if deleted_post:
            flash('Post excluído com sucesso!', 'success')
        else:
            flash('Erro ao excluir post', 'error')
            
    except Exception as e:
        flash(f'Erro ao excluir post: {str(e)}', 'error')
    
    return redirect('/blog')

# Rotas removidas: /profile e /appointments/new para usuários comuns
# Agora apenas psicólogos têm acesso ao sistema completo

# Rotas de redirecionamento para URLs antigas de usuários
@app.route('/register', methods=['GET', 'POST'])
def register_redirect():
    """Redireciona antiga página de registro para explicação de contato direto"""
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login_redirect():
    """Redireciona antiga página de login para explicação de acesso direto"""
    return render_template('login.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile_redirect():
    """Redireciona antiga página de perfil"""
    return render_template('profile.html')

@app.route('/appointments')
@app.route('/appointments/new')
def appointments_redirect():
    """Redireciona antigas páginas de agendamento para contato direto"""
    flash('Para agendar consultas, entre em contato diretamente com nossos psicólogos via WhatsApp!', 'info')
    return redirect('/#doctors')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso', 'success')
    return redirect('/')

# Registrar Blueprint do Dashboard Psicologia
from dashboard_psi import bp as dashboard_psi_bp
app.register_blueprint(dashboard_psi_bp)

# ========================
# ROTAS ADMINISTRATIVAS
# ========================

def is_admin_authenticated():
    """Verificar se o admin está autenticado na sessão"""
    return session.get('admin_authenticated', False)

def admin_required(f):
    """Decorator para verificar autenticação de admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_authenticated():
            flash('Acesso restrito. Faça login como administrador.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Login do administrador"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Verificar credenciais do admin via config
        if (username == app.config['ADMIN_USERNAME'] and 
            password == app.config['ADMIN_PASSWORD']):
            
            session['admin_authenticated'] = True
            session['admin_username'] = username
            flash('Login de administrador realizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Credenciais de administrador inválidas.', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Logout do administrador"""
    session.pop('admin_authenticated', None)
    session.pop('admin_username', None)
    flash('Logout de administrador realizado com sucesso.', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Dashboard administrativo"""
    # Buscar todos os médicos
    doctors = Doctors.query.all()
    
    return render_template('admin_dashboard.html', doctors=doctors)

@app.route('/admin/create-doctor', methods=['GET', 'POST'])
@admin_required
def admin_create_doctor():
    """Formulário para criar novo médico (apenas admin)"""
    if request.method == 'POST':
        try:
            # Extrair dados do formulário
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            name = f"{first_name} {last_name}"
            email = request.form.get('email', '').strip()
            phone_number = request.form.get('phone_number', '').strip()
            crm = request.form.get('crm', '').strip()
            specialty = request.form.get('specialty', '').strip()
            description = request.form.get('description', '').strip()
            address = request.form.get('address', '').strip()
            password = request.form.get('password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()

            # Validações básicas
            if not all([first_name, last_name, email, specialty, password, crm]):
                flash('Todos os campos obrigatórios devem ser preenchidos.', 'error')
                return render_template('admin_create_doctor.html')
            
            if password != confirm_password:
                flash('As senhas não coincidem.', 'error')
                return render_template('admin_create_doctor.html')
            
            if len(password) < 8:
                flash('A senha deve ter pelo menos 8 caracteres.', 'error')
                return render_template('admin_create_doctor.html')

            # Verificar se email já existe
            existing_doctor = Doctors.query.filter_by(email=email).first()
            if existing_doctor:
                flash('Este email já está sendo usado por outro psicólogo.', 'error')
                return render_template('admin_create_doctor.html')

            # Criar hash da senha
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Criar novo médico
            doctors_ctrl = DoctorsController()
            new_doctor = doctors_ctrl.create_doctor(email, name, password, specialty)
            
            if new_doctor:
                # Atualizar campos adicionais
                new_doctor.phone_number = phone_number
                new_doctor.crm = crm
                new_doctor.description = description
                new_doctor.address = address
                new_doctor.password = hashed_password  # Atualizar com senha bcrypt
                
                db.session.commit()
                
                flash(f'Psicólogo {name} cadastrado com sucesso!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Erro ao criar psicólogo. Tente novamente.', 'error')
                
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar psicólogo: {str(e)}', 'error')
    
    return render_template('admin_create_doctor.html')

@app.route('/admin/edit-doctor/<doctor_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_doctor(doctor_id):
    """Formulário para editar médico existente (apenas admin)"""
    doctor = Doctors.query.get_or_404(doctor_id)
    
    if request.method == 'POST':
        try:
            # Extrair dados do formulário
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            name = f"{first_name} {last_name}"
            email = request.form.get('email', '').strip()
            phone_number = request.form.get('phone_number', '').strip()
            crm = request.form.get('crm', '').strip()
            specialty = request.form.get('specialty', '').strip()
            description = request.form.get('description', '').strip()
            address = request.form.get('address', '').strip()
            password = request.form.get('password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()

            # Validações básicas
            if not all([first_name, last_name, email, specialty, crm]):
                flash('Todos os campos obrigatórios devem ser preenchidos.', 'error')
                return render_template('admin_edit_doctor.html', doctor=doctor)
            
            # Validação de senha (só se fornecida)
            if password:
                if password != confirm_password:
                    flash('As senhas não coincidem.', 'error')
                    return render_template('admin_edit_doctor.html', doctor=doctor)
                
                if len(password) < 8:
                    flash('A senha deve ter pelo menos 8 caracteres.', 'error')
                    return render_template('admin_edit_doctor.html', doctor=doctor)

            # Verificar se email já existe (exceto para o próprio médico)
            existing_doctor = Doctors.query.filter(
                Doctors.email == email,
                Doctors.id != doctor_id
            ).first()
            if existing_doctor:
                flash('Este email já está sendo usado por outro psicólogo.', 'error')
                return render_template('admin_edit_doctor.html', doctor=doctor)

            # Atualizar dados do médico
            doctor.name = name
            doctor.email = email
            doctor.phone_number = phone_number or None
            doctor.crm = crm
            doctor.specialty = specialty
            doctor.description = description or None
            doctor.address = address or None
            
            # Atualizar senha se fornecida
            if password:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                doctor.password = hashed_password
                
            db.session.commit()
            
            flash(f'Dados do psicólogo {name} atualizados com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
                
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar psicólogo: {str(e)}', 'error')
    
    return render_template('admin_edit_doctor.html', doctor=doctor)

@app.route('/admin/delete-doctor/<doctor_id>', methods=['POST'])
@admin_required
def admin_delete_doctor(doctor_id):
    """Excluir médico e todos os dados relacionados (apenas admin)"""
    try:
        doctor = Doctors.query.get_or_404(doctor_id)
        doctor_name = doctor.name
        
        # Verificar se existe confirmação de exclusão em cascata
        confirm_cascade = request.form.get('confirm_cascade', False)
        
        # Buscar dados relacionados para mostrar estatísticas
        from dashboard_psi.models import Paciente, Evolucao
        from models.appointments import Appointments
        from models.slots import Slots
        
        pacientes = Paciente.query.filter_by(psicologo_id=doctor_id).all()
        total_pacientes = len(pacientes)
        
        # Contar evoluções de todos os pacientes
        total_evolucoes = 0
        for paciente in pacientes:
            total_evolucoes += paciente.evolucoes.count()
        
        # Contar agendamentos
        agendamentos = Appointments.query.filter_by(doctor_id=doctor_id).all()
        total_agendamentos = len(agendamentos)
        
        # Contar slots
        slots = Slots.query.filter_by(doctor_id=doctor_id).all()
        total_slots = len(slots)
        
        # Se não há confirmação e existem dados relacionados, solicitar confirmação
        if not confirm_cascade and (total_pacientes > 0 or total_agendamentos > 0 or total_slots > 0):
            # Retornar informações para o modal de confirmação
            session['delete_doctor_data'] = {
                'doctor_id': doctor_id,
                'doctor_name': doctor_name,
                'total_pacientes': total_pacientes,
                'total_evolucoes': total_evolucoes,
                'total_agendamentos': total_agendamentos,
                'total_slots': total_slots
            }
            
            flash(f'ATENÇÃO: A exclusão do psicólogo {doctor_name} irá remover permanentemente: '
                  f'{total_pacientes} paciente(s), {total_evolucoes} evolução(ões), '
                  f'{total_agendamentos} agendamento(s) e {total_slots} horário(s). '
                  f'Esta ação NÃO PODE ser desfeita!', 'warning')
            
            return redirect(url_for('admin_dashboard') + f'?show_cascade_modal={doctor_id}')
        
        # Se chegou aqui, é para excluir em cascata
        try:
            # 1. Excluir evoluções de todos os pacientes
            for paciente in pacientes:
                evolucoes = paciente.evolucoes.all()
                for evolucao in evolucoes:
                    db.session.delete(evolucao)
            
            # 2. Excluir pacientes
            for paciente in pacientes:
                db.session.delete(paciente)
            
            # 3. Excluir agendamentos
            for agendamento in agendamentos:
                db.session.delete(agendamento)
            
            # 4. Excluir slots/horários
            for slot in slots:
                db.session.delete(slot)
            
            # 5. Excluir posts do blog (se houver)
            if hasattr(doctor, 'blogs'):
                blog_posts = doctor.blogs.all()
                for post in blog_posts:
                    # Remover arquivo de imagem se existir
                    if post.image_url:
                        import os
                        image_path = os.path.join(app.root_path, 'static', post.image_url.lstrip('/static/'))
                        if os.path.exists(image_path):
                            try:
                                os.remove(image_path)
                            except:
                                pass  # Ignorar erro se não conseguir remover
                    db.session.delete(post)
            
            # 6. Finalmente, excluir o psicólogo
            db.session.delete(doctor)
            
            # Confirmar todas as alterações
            db.session.commit()
            
            # Limpar dados da sessão
            session.pop('delete_doctor_data', None)
            
            # Mensagem de sucesso detalhada
            flash(f'Psicólogo {doctor_name} e todos os dados relacionados foram excluídos com sucesso: '
                  f'{total_pacientes} paciente(s), {total_evolucoes} evolução(ões), '
                  f'{total_agendamentos} agendamento(s) e {total_slots} horário(s) removidos.', 'success')
            
        except Exception as e:
            # Rollback em caso de erro
            db.session.rollback()
            flash(f'Erro durante a exclusão em cascata: {str(e)}', 'error')
            return redirect(url_for('admin_dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir psicólogo: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/transfer-patients/<doctor_id>', methods=['GET', 'POST'])
@admin_required
def admin_transfer_patients(doctor_id):
    """Transferir pacientes de um psicólogo para outro"""
    try:
        doctor = Doctors.query.get_or_404(doctor_id)
        
        # Verificar se há pacientes associados
        from dashboard_psi.models import Paciente
        pacientes = Paciente.query.filter_by(psicologo_id=doctor_id).all()
        
        if not pacientes:
            flash(f'O psicólogo {doctor.name} não possui pacientes para transferir.', 'info')
            return redirect(url_for('admin_dashboard'))
        
        if request.method == 'POST':
            new_doctor_id = request.form.get('new_doctor_id')
            
            if not new_doctor_id:
                flash('Selecione um psicólogo de destino.', 'error')
                return redirect(request.url)
            
            new_doctor = Doctors.query.get(new_doctor_id)
            if not new_doctor:
                flash('Psicólogo de destino não encontrado.', 'error')
                return redirect(request.url)
            
            # Transferir todos os pacientes
            total_transferidos = 0
            for paciente in pacientes:
                paciente.psicologo_id = new_doctor_id
                total_transferidos += 1
            
            db.session.commit()
            
            flash(f'{total_transferidos} paciente(s) transferido(s) de {doctor.name} para {new_doctor.name} com sucesso.', 'success')
            return redirect(url_for('admin_dashboard'))
        
        # GET - Mostrar formulário de transferência
        # Buscar outros psicólogos disponíveis
        outros_psicologos = Doctors.query.filter(Doctors.id != doctor_id).all()
        
        return render_template('admin_transfer_patients.html', 
                             doctor=doctor, 
                             pacientes=pacientes,
                             outros_psicologos=outros_psicologos)
        
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/confirm-cascade-delete', methods=['POST'])
@admin_required
def admin_confirm_cascade_delete():
    """Confirmar exclusão em cascata do psicólogo"""
    try:
        doctor_id = request.form.get('doctor_id')
        confirm_text = request.form.get('confirm_text', '').strip()
        
        if not doctor_id:
            flash('ID do psicólogo não fornecido.', 'error')
            return redirect(url_for('admin_dashboard'))
        
        doctor = Doctors.query.get_or_404(doctor_id)
        
        # Verificar se o usuário digitou "EXCLUIR TUDO" para confirmar
        if confirm_text.upper() != 'EXCLUIR TUDO':
            flash('Para confirmar a exclusão, digite exatamente "EXCLUIR TUDO" no campo de confirmação.', 'error')
            return redirect(url_for('admin_dashboard') + f'?show_cascade_modal={doctor_id}')
        
        # Prosseguir com exclusão em cascata
        from dashboard_psi.models import Paciente, Evolucao
        from models.appointments import Appointments
        from models.slots import Slots
        
        doctor_name = doctor.name
        
        # Buscar todos os dados relacionados
        pacientes = Paciente.query.filter_by(psicologo_id=doctor_id).all()
        agendamentos = Appointments.query.filter_by(doctor_id=doctor_id).all()
        slots = Slots.query.filter_by(doctor_id=doctor_id).all()
        
        # Contadores para relatório
        total_pacientes = len(pacientes)
        total_evolucoes = 0
        total_agendamentos = len(agendamentos)
        total_slots = len(slots)
        
        try:
            # 1. Excluir evoluções de todos os pacientes
            for paciente in pacientes:
                evolucoes = paciente.evolucoes.all()
                total_evolucoes += len(evolucoes)
                for evolucao in evolucoes:
                    db.session.delete(evolucao)
            
            # 2. Excluir pacientes
            for paciente in pacientes:
                db.session.delete(paciente)
            
            # 3. Excluir agendamentos
            for agendamento in agendamentos:
                db.session.delete(agendamento)
            
            # 4. Excluir slots/horários
            for slot in slots:
                db.session.delete(slot)
            
            # 5. Excluir posts do blog (se houver)
            if hasattr(doctor, 'blogs'):
                blog_posts = doctor.blogs.all()
                for post in blog_posts:
                    # Remover arquivo de imagem se existir
                    if post.image_url:
                        import os
                        image_path = os.path.join(app.root_path, 'static', post.image_url.lstrip('/static/'))
                        if os.path.exists(image_path):
                            try:
                                os.remove(image_path)
                            except:
                                pass  # Ignorar erro se não conseguir remover
                    db.session.delete(post)
            
            # 6. Finalmente, excluir o psicólogo
            db.session.delete(doctor)
            
            # Confirmar todas as alterações
            db.session.commit()
            
            # Mensagem de sucesso detalhada
            flash(f'✅ EXCLUSÃO CONCLUÍDA: Psicólogo {doctor_name} e todos os dados relacionados foram excluídos permanentemente: '
                  f'{total_pacientes} paciente(s), {total_evolucoes} evolução(ões), '
                  f'{total_agendamentos} agendamento(s) e {total_slots} horário(s) removidos.', 'success')
            
        except Exception as e:
            # Rollback em caso de erro
            db.session.rollback()
            flash(f'❌ Erro durante a exclusão em cascata: {str(e)}', 'error')
        
    except Exception as e:
        flash(f'Erro na confirmação de exclusão: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/doctor-info/<doctor_id>')
@admin_required
def admin_doctor_info(doctor_id):
    """Retornar informações do psicólogo em JSON para o modal"""
    try:
        doctor = Doctors.query.get_or_404(doctor_id)
        
        # Buscar dados relacionados
        from dashboard_psi.models import Paciente, Evolucao
        from models.appointments import Appointments
        from models.slots import Slots
        
        pacientes = Paciente.query.filter_by(psicologo_id=doctor_id).all()
        total_pacientes = len(pacientes)
        
        # Contar evoluções
        total_evolucoes = 0
        for paciente in pacientes:
            total_evolucoes += paciente.evolucoes.count()
        
        # Contar agendamentos e slots
        total_agendamentos = Appointments.query.filter_by(doctor_id=doctor_id).count()
        total_slots = Slots.query.filter_by(doctor_id=doctor_id).count()
        
        return jsonify({
            'id': doctor.id,
            'name': doctor.name,
            'email': doctor.email,
            'patients_count': total_pacientes,
            'evolucoes_count': total_evolucoes,
            'appointments_count': total_agendamentos,
            'slots_count': total_slots
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sitemap.xml')
def sitemap_xml():
    return sitemap.generate()

if __name__ == '__main__':
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        print("Tabelas criadas com sucesso!")
    
    app.run(debug=config.DEBUG, host='0.0.0.0', port=8000)