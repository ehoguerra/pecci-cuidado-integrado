from db import db
from models.appointments import Appointments
from models.user import User
from models.doctors import Doctors
from models.slots import Slots
from controllers.slot_controller import SlotsController
import uuid

class UserController:
    def __init__(self):
        self.db = db

    def get_user_by_id(self, user_id):
        return self.db.session.query(User).filter_by(id=user_id).first()

    def create_user(self, email, name, password):
        new_user = User(id=str(uuid.uuid4())[:20], email=email, name=name, password=password)
        self.db.session.add(new_user)
        self.db.session.commit()
        return new_user

    def update_user(self, user_id, **kwargs):
        user = self.get_user_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            self.db.session.commit()
            return user
        return None

    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        if user:
            self.db.session.delete(user)
            self.db.session.commit()
            return True
        return False
    
    def get_all_users(self):
        return self.db.session.query(User).all()
    
    def authenticate_user(self, email, password):
        user = self.db.session.query(User).filter_by(email=email, password=password).first()
        return user if user else None
    
    def increment_appointment_count(self, user_id):
        user = self.get_user_by_id(user_id)
        if user:
            user.appointment_count += 1
            self.db.session.commit()
            return user.appointment_count
        return None
    
    def get_user_appointments(self, user_id):
        return self.db.session.query(Appointments).filter_by(user_id=user_id).all()
    
    def get_user_slots(self, user_id):
        return self.db.session.query(Slots).join(Appointments).filter(Appointments.user_id == user_id).all()
