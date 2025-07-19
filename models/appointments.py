from db import db

class Appointments(db.Model):
    __tablename__ = 'appointments'

    appointment_id = db.Column(db.String(15), primary_key=True, nullable=False)
    user_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.String(20), db.ForeignKey('doctors.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled', nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())