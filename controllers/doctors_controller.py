from db import db
from models.appointments import Appointments
from models.user import User
from models.doctors import Doctors
from models.slots import Slots
from controllers.slot_controller import SlotsController
import uuid

class DoctorsController:
    def __init__(self):
        self.db = db

    def get_doctor_by_email(self, email):
        return self.db.session.query(Doctors).filter_by(email=email).first()

    def get_doctor_by_id(self, doctor_id):
        return self.db.session.query(Doctors).filter_by(id=doctor_id).first()

    def create_doctor(self, email, name, password, specialty, phone_number=None, profile_pic=None, description=None, address=None, crm=None):
        new_doctor = Doctors(
            id=str(uuid.uuid4())[:20], 
            email=email, 
            name=name, 
            password=password, 
            profile_picture=profile_pic,
            specialty=specialty,
            phone_number=phone_number,
            description=description,
            address=address,
            crm=crm
        )
        
        self.db.session.add(new_doctor)
        self.db.session.commit()
        return new_doctor

    def update_doctor(self, doctor_id, **kwargs):
        doctor = self.get_doctor_by_id(doctor_id)
        if doctor:
            for key, value in kwargs.items():
                setattr(doctor, key, value)
            self.db.session.commit()
            return doctor
        return None

    def delete_doctor(self, doctor_id):
        doctor = self.get_doctor_by_id(doctor_id)
        if doctor:
            self.db.session.delete(doctor)
            self.db.session.commit()
            return True
        return False
    
    def get_all_doctors(self):
        return self.db.session.query(Doctors).all()
    
    def get_doctor_appointments(self, doctor_id):
        return self.db.session.query(Appointments).filter_by(doctor_id=doctor_id).all()
    
    def increment_appointment_count(self, doctor_id):
        doctor = self.get_doctor_by_id(doctor_id)
        if doctor:
            doctor.appointment_count += 1
            self.db.session.commit()
            return doctor.appointment_count
        return None

    def get_doctor_by_specialty(self, specialty):
        return self.db.session.query(Doctors).filter_by(specialty=specialty).all()
    
    def authenticate_doctor(self, email, password):
        doctor = self.db.session.query(Doctors).filter_by(email=email, password=password).first()
        return doctor if doctor else None
    
    def doctor_free_slots(self, doctor_id):
        doctor = self.get_doctor_by_id(doctor_id)
        if doctor:
            return SlotsController().get_free_slots_by_doctor(doctor_id)
        return None
    
    def get_doctor_data(self, doctor_id):
        doctor = self.get_doctor_by_id(doctor_id)
        if doctor:
            return {
                'id': doctor.id,
                'email': doctor.email,
                'name': doctor.name,
                'specialty': doctor.specialty,
                'phone_number': doctor.phone_number,
                'description': doctor.description,
                'address': doctor.address,
                'crm': doctor.crm,
                'free_slots': doctor.free_slots,
                'appointment_count': doctor.appointment_count
            }
        return None