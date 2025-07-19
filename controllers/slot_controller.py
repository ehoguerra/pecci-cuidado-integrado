from db import db
from models.slots import Slots
from models.appointments import Appointments
from models.user import User
from models.doctors import Doctors
import uuid

class SlotsController:
    def __init__(self):
        self.db = db

    def get_slot_by_id(self, slot_id):
        return self.db.session.query(Slots).filter_by(slot_id=slot_id).first()
    
    def get_slots_by_doctor_and_date(self, doctor_id, appointment_date):
        return self.db.session.query(Slots).filter_by(doctor_id=doctor_id, appointment_date=appointment_date).all()

    def create_slot(self, doctor_id, appointment_date, start_time, end_time, appointment_type=None, price=None, notes=None):
        new_slot = Slots(
            slot_id=str(uuid.uuid4())[:20],  # Generate a unique slot_id
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_time,
            appointment_type=appointment_type,
            price=price,
            notes=notes
        )
        self.db.session.add(new_slot)
        self.db.session.commit()
        return new_slot

    def update_slot(self, slot_id, **kwargs):
        slot = self.get_slot_by_id(slot_id)
        if slot:
            for key, value in kwargs.items():
                setattr(slot, key, value)
            self.db.session.commit()
            return slot
        return None

    def delete_slot(self, slot_id):
        slot = self.get_slot_by_id(slot_id)
        if slot:
            self.db.session.delete(slot)
            self.db.session.commit()
            return True
        return False
    
    def get_all_slots(self):
        return self.db.session.query(Slots).all()
    
    def get_free_slots_by_doctor(self, doctor_id):
        slots = self.db.session.query(Slots).filter_by(doctor_id=doctor_id, is_booked=False).all()
        slot_dict = {}
        for slot in slots:
            date_key = slot.appointment_date.strftime('%Y-%m-%d')
            if date_key not in slot_dict:
                slot_dict[date_key] = []
            slot_dict[date_key].append({
                'slot_id': slot.slot_id,
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
                'appointment_type': slot.appointment_type,
                'price': slot.price,
                'notes': slot.notes
            })
        
        # Converter para o formato esperado pelo template
        result = []
        for date_str, slots_list in slot_dict.items():
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            weekday_names = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
            weekday_name = weekday_names[date_obj.weekday()]
            
            result.append({
                'date': date_str,
                'day': weekday_name,
                'formatted_date': date_obj.strftime('%d/%m/%Y'),
                'slots': slots_list
            })
        
        return sorted(result, key=lambda x: x['date'])

    def get_slots_by_doctor(self, doctor_id):
        return self.db.session.query(Slots).filter_by(doctor_id=doctor_id).all()
    
    def get_slots_by_weekday(self, doctor_id, weekday):
        return self.db.session.query(Slots).filter(
            Slots.doctor_id == doctor_id,
            Slots.appointment_date == weekday
        ).all()
    
    def book_slot(self, slot_id, user_id):
        slot = self.get_slot_by_id(slot_id)
        if slot and not slot.is_booked:
            slot.is_booked = True
            appointment = Appointments(
                appointment_id=str(uuid.uuid4())[:15],
                user_id=user_id,
                doctor_id=slot.doctor_id,
                appointment_date=slot.appointment_date
            )
            self.db.session.add(appointment)
            self.db.session.commit()
            return slot, appointment
        return None, None
    
    def get_slot_by_doctor_date_time(self, doctor_id, appointment_date, start_time):
        """Busca um slot específico por médico, data e horário"""
        return self.db.session.query(Slots).filter_by(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            start_time=start_time
        ).first()
    
    def get_available_slots_by_date(self, doctor_id, appointment_date):
        """Busca slots disponíveis (não reservados) para uma data específica"""
        from datetime import datetime
        if isinstance(appointment_date, str):
            appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        
        return self.db.session.query(Slots).filter_by(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            is_booked=False
        ).order_by(Slots.start_time).all()