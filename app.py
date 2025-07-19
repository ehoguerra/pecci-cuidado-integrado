from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from db import db, migrate

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
import config
from models.slots import Slots


import bcrypt
from decimal import Decimal, ROUND_HALF_UP

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)
migrate.init_app(app, db)
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            first_name = request.form['first_name']
            last_name = request.form['last_name'] 
            email = request.form['email']
            phone = request.form.get('phone', '')
            birth_date = request.form.get('birth_date', None)
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            
            # Validações básicas
            if password != confirm_password:
                flash('As senhas não coincidem', 'error')
                return render_template('register.html')
            
            # Verificar se o email já existe
            user_controller = UserController()
            existing_user = db.session.query(User).filter_by(email=email).first()
            if existing_user:
                flash('Este email já está cadastrado', 'error')
                return render_template('register.html')
            
            # Criar hash da senha
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Criar usuário
            full_name = f"{first_name} {last_name}"
            new_user = user_controller.create_user(email, full_name, hashed_password)

            # Corrigir data de nascimento para database
            if birth_date:
                from datetime import datetime
                birth_date = datetime.strptime(birth_date, '%d-%m-%Y').date()
            
            # Atualizar campos adicionais se fornecidos
            if phone or birth_date:
                update_data = {}
                if phone:
                    update_data['phone_number'] = phone
                if birth_date:
                    from datetime import datetime
                    update_data['birth_date'] = datetime.strptime(birth_date, '%d-%m-%Y').date()
                
                user_controller.update_user(new_user.id, **update_data)
            
            session['user_id'] = new_user.id
            session['user_name'] = new_user.name
            session['user_email'] = new_user.email

            return redirect('/app')

        except Exception as e:
            flash(f'Erro ao criar conta: {str(e)}', 'error')
            return render_template('register.html', error=str(e))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = request.form.get('remember', False)
        
        try:
            # Buscar usuário
            user = db.session.query(User).filter_by(email=email).first()
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_email'] = user.email
                
                if remember:
                    session.permanent = True
                
                flash(f'Bem-vindo, {user.name}!', 'success')
                return redirect('/')
            else:
                flash('Email ou senha inválidos', 'error')
                
        except Exception as e:
            flash(f'Erro no login: {str(e)}', 'error')
    
    return render_template('login.html')

@app.route('/appointments', methods=['GET'])
def appointments():
    if 'user_id' not in session:
        flash('Você precisa estar logado para acessar esta página', 'error')
        return redirect('/login')
    
    user_id = session['user_id']
    user_name = session.get('user_name', 'Usuário')
    user_email = session.get('user_email', 'Email não disponível')

    # Buscar todos os agendamentos do usuário
    user_controller = UserController()
    appointments = user_controller.get_user_appointments(user_id)
    
    return render_template('appointments.html', appointments=appointments)

@app.route('/create_doctor', methods=['GET', 'POST'])
def create_doctor():
    if request.method == 'POST':
        try:
            # Extrair dados do formulário
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            name = f"{first_name} {last_name}"
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            crm = request.form.get('crm', '').strip()
            specialty = request.form.get('specialty', '').strip()
            description = request.form.get('description', '').strip()
            address = request.form.get('address', '').strip()
            password = request.form.get('password', '').strip()
            profile_pic = request.files.get('profile_photo', None)

            # Pic filename and path
            if profile_pic:
                if profile_pic.filename == '':
                    flash('Nenhuma foto selecionada', 'error')
                    return render_template('create_doctor.html')
                
                # Validar extensão do arquivo
                allowed_extensions = app.config['ALLOWED_EXTENSIONS']
                if not any(profile_pic.filename.lower().endswith(ext) for ext in allowed_extensions):
                    flash('Formato de imagem inválido. Use JPG, PNG ou GIF.', 'error')
                    return render_template('create_doctor.html')
                
                # Salvar foto no diretório de upload
                profile_pic_path = f"{app.config['UPLOAD_FOLDER']}/{email}"
                profile_pic.save(profile_pic_path)

            # Validar campos obrigatórios
            if not all([first_name, last_name, email, specialty, password, crm]):
                flash('Por favor, preencha todos os campos obrigatórios', 'error')
                return render_template('create_doctor.html')
            
            # Hash da senha
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Criar médico
            doctors_controller = DoctorsController()
            new_doctor = doctors_controller.create_doctor(
                email=email,
                name=name,
                password=hashed_password,
                specialty=specialty,
                profile_pic=profile_pic_path if profile_pic else None,
                phone_number=phone,
                description=description,
                address=address,
                crm=crm
            )
            
            flash(f'Médico(a) {name} cadastrado(a) com sucesso!', 'success')
            return redirect('/doctors')
        
        except Exception as e:
            flash(f'Erro ao cadastrar médico: {str(e)}', 'error')
            return render_template('create_doctor.html')
    
    return render_template('create_doctor.html')

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
def psychologist_dashboard():
    # Verificar se o psicólogo está logado
    if 'doctor_id' not in session:
        flash('Você precisa estar logado como psicólogo para acessar o dashboard', 'error')
        return redirect('/p/login')
    
    # Buscar dados do psicólogo logado
    doctors_controller = DoctorsController()
    doctor_id = session['doctor_id']
    doctor = doctors_controller.get_doctor_by_id(session['doctor_id'])
    
    if not doctor:
        flash('Psicólogo não encontrado', 'error')
        session.clear()
        return redirect('/p/login')
    
    # Dados do psicólogo
    psychologist_data = {
        'id': doctor.id,
        'name': doctor.name,
        'specialty': doctor.specialty,
        'email': doctor.email,
        'crp': doctor.crm or 'CRP não informado',
        'phone': doctor.phone_number or 'Telefone não informado',
        'address': doctor.address or 'Endereço não informado',
        'description': doctor.description or 'Descrição não informada'
    }
    
    # Estatísticas do dashboard
    apController = AppointmentsController()
    stats = apController.get_monthly_stats(doctor_id)
    
    # Consultas de hoje (dados reais)
    today_appointments = apController.get_todays_appointments(doctor_id)
    
    # Pacientes ativos (dados reais)
    patients = apController.get_doctors_patients(doctor_id)
    
    # Horários disponíveis da semana
    slController = SlotsController()
    available_slots = slController.get_free_slots_by_doctor(doctor_id=session['doctor_id'])

    # Buscar todos os usuários para seleção de pacientes
    userController = UserController()
    users = userController.get_all_users()

    # Yesterdays appointments
    yesterdays_appointments = apController.get_yesterdays_appointments_count(doctor_id)

    #print("Available slots:", available_slots)

    # if not available_slots:
    #     available_slots = [
    #         {'day': 'Segunda', 'date': '2025-07-21', 'slots': ['14:00', '15:30', '17:00']},
    #         {'day': 'Terça', 'date': '2025-07-22', 'slots': ['09:00', '10:30', '16:00']},
    #         {'day': 'Quarta', 'date': '2025-07-23', 'slots': ['08:30', '14:00', '15:30']},
    #         {'day': 'Quinta', 'date': '2025-07-24', 'slots': ['10:00', '11:30', '16:30']},
    #         {'day': 'Sexta', 'date': '2025-07-25', 'slots': ['09:30', '14:30', '16:00']}
    #     ]
    
    return render_template('psychologist_dashboard.html', 
                         psychologist=psychologist_data,
                         stats=stats,
                         today_appointments=today_appointments,
                         patients=patients,
                         available_slots=available_slots,
                         users=users,
                         yesterdays_appointments=yesterdays_appointments)

@app.route('/p/login', methods=['GET', 'POST'])
def p_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = request.form.get('remember', False)
        
        try:
            # Buscar psicólogo no banco de dados
            doctors_controller = DoctorsController()
            doctor = db.session.query(Doctors).filter_by(email=email).first()
            
            if doctor and bcrypt.checkpw(password.encode('utf-8'), doctor.password.encode('utf-8')):
                # Login de psicólogo bem-sucedido
                session['doctor_id'] = doctor.id
                session['doctor_name'] = doctor.name
                session['doctor_email'] = doctor.email
                session['doctor_specialty'] = doctor.specialty
                session['doctor_crp'] = doctor.crm  # Assumindo que crm armazena o CRP
                
                if remember:
                    session.permanent = True
                
                flash(f'Bem-vindo ao dashboard, Dr(a). {doctor.name}!', 'success')
                return redirect('/psychologist_dashboard')
            else:
                flash('Email ou senha inválidos para psicólogo', 'error')
                
        except Exception as e:
            flash(f'Erro no login do psicólogo: {str(e)}', 'error')
    
    return render_template('psychologist_login.html')

@app.route('/create_schedule', methods=['POST'])
def create_schedule():
    # Verificar se o psicólogo está logado
    if 'doctor_id' not in session:
        flash('Você precisa estar logado como psicólogo para cadastrar horários', 'error')
        return redirect('/p/login')
    
    try:
        doctor_id = session['doctor_id']
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
            return redirect('/psychologist_dashboard')
        
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
    
    return redirect('/psychologist_dashboard')

@app.route('/create_appointment', methods=['POST'])
def create_appointment():
    if 'doctor_id' not in session:
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
        
        doctor_id = session['doctor_id']
        
        # Validar dados obrigatórios
        if not all([patient_id, appointment_date, appointment_time, appointment_type]):
            flash('Por favor, preencha todos os campos obrigatórios', 'error')
            return redirect('/psychologist_dashboard')
        
        # Verificar se o paciente existe
        userController = UserController()
        patient = userController.get_user_by_id(patient_id)
        if not patient:
            flash('Paciente não encontrado', 'error')
            return redirect('/psychologist_dashboard')
        
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
    
    return redirect('/psychologist_dashboard')

@app.route('/get_available_times', methods=['POST'])
def get_available_times():
    if 'doctor_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    try:
        data = request.get_json()
        selected_date = data.get('date')
        doctor_id = session['doctor_id']
        
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
def get_patient_info():
    if 'doctor_id' not in session:
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
    is_doctor = 'doctor_id' in session
    doctor_name = session.get('doctor_name', 'Usuário') if is_doctor else None

    return render_template('blog.html', posts=posts, recent_posts=recent_posts, is_doctor=is_doctor, doctor_name=doctor_name)

@app.route('/blog/create', methods=['GET', 'POST'])
def create_blog_post():
    # Verificar se é um doutor logado
    if 'doctor_id' not in session:
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
                author_id=session['doctor_id'],
                image_url=image_url
            )
            
            flash('Post criado com sucesso!', 'success')
            return redirect('/blog')
            
        except Exception as e:
            flash(f'Erro ao criar post: {str(e)}', 'error')
    
    return render_template('create_blog_post.html')

@app.route('/blog/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_blog_post(post_id):
    # Verificar se é um doutor logado
    if 'doctor_id' not in session:
        flash('Apenas psicólogos podem editar posts', 'error')
        return redirect('/blog')
    
    blog_controller = BlogController()
    post = blog_controller.get_post_by_id(post_id)
    
    if not post:
        flash('Post não encontrado', 'error')
        return redirect('/blog')
    
    # Verificar se o doutor é o autor do post
    if post.author_id != session['doctor_id']:
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
    is_doctor = 'doctor_id' in session
    
    return render_template('view_blog_post.html', post=post, recent_posts=recent_posts, is_doctor=is_doctor)

@app.route('/blog/delete/<int:post_id>', methods=['POST'])
def delete_blog_post(post_id):
    # Verificar se é um doutor logado
    if 'doctor_id' not in session:
        flash('Apenas psicólogos podem excluir posts', 'error')
        return redirect('/blog')
    
    try:
        blog_controller = BlogController()
        post = blog_controller.get_post_by_id(post_id)
        
        if not post:
            flash('Post não encontrado', 'error')
            return redirect('/blog')
        
        # Verificar se o doutor é o autor do post
        if post.author_id != session['doctor_id']:
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

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Você precisa estar logado para acessar esta página', 'error')
        return redirect('/login')
    
    user_id = session['user_id']
    user_controller = UserController()
    
    if request.method == 'POST':
        try:
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            birth_date = request.form.get('birth_date', None)
            
            # Validar campos obrigatórios
            if not first_name or not last_name or not email:
                flash('Por favor, preencha todos os campos obrigatórios', 'error')
                return redirect('/profile')
            
            # Atualizar usuário
            user_controller.update_user(
                user_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone,
                birth_date=birth_date
            )
            
            # Atualizar também o nome completo no banco
            full_name = f"{first_name} {last_name}"
            user_controller.update_user(user_id, name=full_name)
            
            session['user_name'] = full_name
            session['user_email'] = email
            
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect('/profile')
        
        except Exception as e:
            flash(f'Erro ao atualizar perfil: {str(e)}', 'error')
    
    # Buscar dados do usuário
    user = user_controller.get_user_by_id(user_id)
    
    return render_template('profile.html', user=user)

@app.route('/appointments/new', methods=['GET', 'POST'])
def new_appointment():
    if 'user_id' not in session:
        flash('Você precisa estar logado para agendar uma consulta', 'error')
        return redirect('/login')
    
    if request.method == 'POST':
        try:
            doctor_id = request.form.get('doctor_id')
            appointment_date = request.form.get('appointment_date')
            appointment_time = request.form.get('appointment_time')
            appointment_type = request.form.get('appointment_type')
            
            if not doctor_id or not appointment_date or not appointment_time or not appointment_type:
                flash('Por favor, preencha todos os campos obrigatórios', 'error')
                return redirect('/appointments/new')
            
            # Criar agendamento
            appointments_controller = AppointmentsController()
            new_appointment = appointments_controller.create_appointment(
                user_id=session['user_id'],
                doctor_id=doctor_id,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                appointment_type=appointment_type
            )
            
            flash('Consulta agendada com sucesso!', 'success')
            return redirect('/appointments')
        
        except Exception as e:
            flash(f'Erro ao agendar consulta: {str(e)}', 'error')
    
    # Buscar todos os médicos disponíveis
    doctors = DoctorsController().get_all_doctors()
    
    return render_template('new_appointment.html', doctors=doctors)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso', 'success')
    return redirect('/')


if __name__ == '__main__':
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        print("Tabelas criadas com sucesso!")
    
    app.run(debug_mode=config.DEBUG, host='0.0.0.0', port=8000)