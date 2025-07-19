from db import db

class Slots(db.Model):
    __tablename__ = 'slots'

    slot_id = db.Column(db.String(20), primary_key=True, nullable=False)
    doctor_id = db.Column(db.String(20), db.ForeignKey('doctors.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    appointment_type = db.Column(db.String(50), nullable=True)  # individual, couple, family, group
    price = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_booked = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())