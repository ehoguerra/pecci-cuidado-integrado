from db import db
from models.appointments import Appointments
from models.user import User
from models.doctors import Doctors
from sqlalchemy import func, distinct
import uuid
import datetime

class AppointmentsController:
    def __init__(self):
        self.db = db
    
    def get_appointment_by_id(self, appointment_id):
        return self.db.session.query(Appointments).filter_by(appointment_id=appointment_id).first()
    
    def create_appointment(self, user_id, doctor_id, appointment_date, appointment_time=None, appointment_type=None, notes=None, price=None, duration=None):
        # Combinar data e hora se fornecidos separadamente
        if appointment_time and isinstance(appointment_date, str):
            import datetime
            appointment_datetime = datetime.datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
        elif isinstance(appointment_date, str):
            import datetime
            appointment_datetime = datetime.datetime.strptime(appointment_date, "%Y-%m-%d")
        else:
            appointment_datetime = appointment_date
            
        new_appointment = Appointments(
            appointment_id=str(uuid.uuid4())[:15],
            user_id=user_id,
            doctor_id=doctor_id,
            appointment_date=appointment_datetime
        )
        self.db.session.add(new_appointment)
        self.db.session.commit()
        return new_appointment
    def update_appointment(self, appointment_id, **kwargs):
        appointment = self.get_appointment_by_id(appointment_id)
        if appointment:
            for key, value in kwargs.items():
                setattr(appointment, key, value)
            self.db.session.commit()
            return appointment
        return None
    def delete_appointment(self, appointment_id):
        appointment = self.get_appointment_by_id(appointment_id)
        if appointment:
            self.db.session.delete(appointment)
            self.db.session.commit()
            return True
        return False
    def get_all_appointments(self):
        return self.db.session.query(Appointments).all()
    def get_appointments_by_user(self, user_id):
        return self.db.session.query(Appointments).filter_by(user_id=user_id).all()
    def get_appointments_by_doctor(self, doctor_id):
        return self.db.session.query(Appointments).filter_by(doctor_id=doctor_id).all()
    def get_appointments_by_date(self, appointment_date):
        return self.db.session.query(Appointments).filter(Appointments.appointment_date == appointment_date).all()
    def change_appointment_status(self, appointment_id, status):
        appointment = self.get_appointment_by_id(appointment_id)
        if appointment:
            appointment.status = status
            self.db.session.commit()
            return appointment
        return None
    def increment_user_appointment_count(self, user_id):
        user = self.db.session.query(User).filter_by(id=user_id).first()
        if user:
            user.appointment_count += 1
            self.db.session.commit()
            return user.appointment_count
        return None
    
    def increment_doctor_appointment_count(self, doctor_id):
        doctor = self.db.session.query(Doctors).filter_by(id=doctor_id).first()
        if doctor:
            doctor.appointment_count += 1
            self.db.session.commit()
            return doctor.appointment_count
        return None
    def authenticate_appointment(self, user_id, doctor_id, appointment_date):
        appointment = self.db.session.query(Appointments).filter_by(user_id=user_id, doctor_id=doctor_id, appointment_date=appointment_date).first()
        return appointment if appointment else None
    def get_appointments_by_status(self, status):
        return self.db.session.query(Appointments).filter_by(status=status).all()
    def get_upcoming_appointments(self, user_id):
        return self.db.session.query(Appointments).filter(Appointments.user_id == user_id, Appointments.appointment_date > db.func.now()).all()
    def get_past_appointments(self, user_id):
        return self.db.session.query(Appointments).filter(Appointments.user_id == user_id, Appointments.appointment_date <= db.func.now()).all()
    def get_appointments_by_user_and_date(self, user_id, appointment_date):
        return self.db.session.query(Appointments).filter(Appointments.user_id == user_id, Appointments.appointment_date == appointment_date).all()
    def get_appointments_by_doctor_and_date(self, doctor_id, appointment_date):
        return self.db.session.query(Appointments).filter(Appointments.doctor_id == doctor_id, Appointments.appointment_date == appointment_date).all()
    def get_appointments_by_user_and_doctor(self, user_id, doctor_id):
        return self.db.session.query(Appointments).filter(Appointments.user_id == user_id, Appointments.doctor_id == doctor_id).all()
    def get_appointments_by_user_and_status(self, user_id, status):
        return self.db.session.query(Appointments).filter(Appointments.user_id == user_id, Appointments.status == status).all()
    def get_appointments_by_doctor_and_status(self, doctor_id, status):
        return self.db.session.query(Appointments).filter(Appointments.doctor_id == doctor_id, Appointments.status == status).all()
    def get_appointments_by_date_range(self, start_date, end_date):
        return self.db.session.query(Appointments).filter(Appointments.appointment_date >= start_date, Appointments.appointment_date <= end_date).all()
    def get_appointments_by_user_and_date_range(self, user_id, start_date, end_date):
        return self.db.session.query(Appointments).filter(Appointments.user_id == user_id, Appointments.appointment_date >= start_date, Appointments.appointment_date <= end_date).all()
    def get_appointments_by_doctor_and_date_range(self, doctor_id, start_date, end_date):
        return self.db.session.query(Appointments).filter(Appointments.doctor_id == doctor_id, Appointments.appointment_date >= start_date, Appointments.appointment_date <= end_date).all()
    def get_appointments_by_user_doctor_and_date(self, user_id, doctor_id, appointment_date):
        return self.db.session.query(Appointments).filter(Appointments.user_id == user_id, Appointments.doctor_id == doctor_id, Appointments.appointment_date == appointment_date).all()
    def get_appointments_by_user_doctor_and_status(self, user_id, doctor_id, status):
        return self.db.session.query(Appointments).filter(Appointments.user_id == user_id, Appointments.doctor_id == doctor_id, Appointments.status == status).all()
    def get_doctors_patients(self, doctor_id):
        """Retorna uma lista de pacientes únicos do doutor com informações adicionais"""
        from sqlalchemy import func, distinct
        from datetime import datetime
        
        # Buscar pacientes únicos que têm consultas com este doutor
        patients_data = self.db.session.query(
            User.id,
            User.name,
            User.email,
            User.phone_number,
            User.birth_date,
            func.count(Appointments.appointment_id).label('total_sessions'),
            func.max(Appointments.appointment_date).label('last_appointment')
        ).join(
            Appointments, User.id == Appointments.user_id
        ).filter(
            Appointments.doctor_id == doctor_id
        ).group_by(
            User.id, User.name, User.email, User.phone_number, User.birth_date
        ).all()
        
        # Formatar dados para o template
        patients = []
        for patient_data in patients_data:
            age = None
            if patient_data.birth_date:
                today = datetime.now().date()
                age = today.year - patient_data.birth_date.year
                if today.month < patient_data.birth_date.month or (today.month == patient_data.birth_date.month and today.day < patient_data.birth_date.day):
                    age -= 1
            
            patients.append({
                'id': patient_data.id,
                'name': patient_data.name,
                'email': patient_data.email,
                'phone': patient_data.phone_number or 'Não informado',
                'age': age or 'Não informado',
                'total_sessions': patient_data.total_sessions,
                'last_appointment': patient_data.last_appointment.strftime('%d/%m/%Y') if patient_data.last_appointment else 'Nunca',
                'status': 'active'  # Por padrão, consideramos ativo
            })
        
        return patients
    
    def get_todays_appointments(self, doctor_id):
        """Retorna as consultas de hoje para o doutor"""
        from datetime import datetime, date
        
        today = date.today()
        
        appointments = self.db.session.query(
            Appointments.appointment_id,
            Appointments.appointment_date,
            Appointments.status,
            User.name.label('patient_name'),
            User.phone_number.label('patient_phone')
        ).join(
            User, Appointments.user_id == User.id
        ).filter(
            Appointments.doctor_id == doctor_id,
            func.date(Appointments.appointment_date) == today
        ).order_by(Appointments.appointment_date).all()
        
        # Formatar dados para o template
        formatted_appointments = []
        for apt in appointments:
            formatted_appointments.append({
                'id': apt.appointment_id,
                'time': apt.appointment_date.strftime('%H:%M'),
                'patient_name': apt.patient_name,
                'appointment_type': 'Consulta Individual',  # Valor padrão
                'status': apt.status,
                'patient_phone': apt.patient_phone or 'Não informado'
            })
        
        return formatted_appointments
    
    def get_monthly_stats(self, doctor_id):
        """Retorna estatísticas mensais do doutor"""
        from datetime import datetime, date, timedelta
        from calendar import monthrange
        
        today = date.today()
        month_start = today.replace(day=1)
        # Encontrar o último dia do mês
        _, last_day = monthrange(today.year, today.month)
        month_end = today.replace(day=last_day)
        
        # Consultas do mês
        total_appointments_month = self.db.session.query(Appointments).filter(
            Appointments.doctor_id == doctor_id,
            func.date(Appointments.appointment_date) >= month_start,
            func.date(Appointments.appointment_date) <= month_end
        ).count()
        
        # Consultas de hoje
        appointments_today = self.db.session.query(Appointments).filter(
            Appointments.doctor_id == doctor_id,
            func.date(Appointments.appointment_date) == today
        ).count()
        
        # Pacientes ativos (únicos do mês)
        active_patients = self.db.session.query(func.count(func.distinct(Appointments.user_id))).filter(
            Appointments.doctor_id == doctor_id,
            func.date(Appointments.appointment_date) >= month_start,
            func.date(Appointments.appointment_date) <= month_end
        ).scalar() or 0
        
        # Novos pacientes do mês (primeira consulta no mês)
        # Por simplicidade, vamos contar todos os pacientes únicos do mês
        new_patients_month = max(0, active_patients - 5)  # Estimativa simples
        
        return {
            'appointments_today': appointments_today,
            'active_patients': active_patients,
            'total_appointments_month': total_appointments_month,
            'new_patients_month': new_patients_month,
            'available_slots': 12,  # Será calculado depois
            'attendance_rate': 95,  # Será calculado depois
            'earnings_month': 0.0   # Será calculado depois
        }
    def get_yesterdays_appointments(self, doctor_id):
        """Retorna as consultas de ontem para o doutor"""
        from datetime import datetime, timedelta
        
        yesterday = datetime.now() - timedelta(days=1)
        
        appointments = self.db.session.query(
            Appointments.appointment_id,
            Appointments.appointment_date,
            Appointments.status,
            User.name.label('patient_name'),
            User.phone_number.label('patient_phone')
        ).join(
            User, Appointments.user_id == User.id
        ).filter(
            Appointments.doctor_id == doctor_id,
            func.date(Appointments.appointment_date) == yesterday.date()
        ).order_by(Appointments.appointment_date).all()
        
        # Formatar dados para o template
        formatted_appointments = []
        for apt in appointments:
            formatted_appointments.append({
                'id': apt.appointment_id,
                'time': apt.appointment_date.strftime('%H:%M'),
                'patient_name': apt.patient_name,
                'appointment_type': 'Consulta Individual',  # Valor padrão
                'status': apt.status,
                'patient_phone': apt.patient_phone or 'Não informado'
            })
        
        return formatted_appointments
    
    def get_yesterdays_appointments_count(self, doctor_id):
        """Retorna a contagem de consultas de ontem para o doutor"""
        from datetime import datetime, timedelta
        
        yesterday = datetime.now() - timedelta(days=1)
        
        count = self.db.session.query(Appointments).filter(
            Appointments.doctor_id == doctor_id,
            func.date(Appointments.appointment_date) == yesterday.date()
        ).count()
        
        return count