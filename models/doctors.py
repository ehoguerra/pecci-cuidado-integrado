from db import db
from flask_login import UserMixin

class Doctors(UserMixin, db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.String(20), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    free_slots = db.Column(db.Integer, default=0, nullable=False)
    appointment_count = db.Column(db.Integer, default=0, nullable=False)
    profile_picture = db.Column(db.String(200), nullable=True)
    description = db.Column(db.String(500), nullable=True)
    phone_number = db.Column(db.String(30), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    specialty = db.Column(db.String(50), nullable=False)
    crm = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Relacionamento com posts do blog
    blogs = db.relationship('BlogModel', back_populates='author', lazy='dynamic')
    
    # Relacionamento com pacientes (dashboard psicológico)
    pacientes = db.relationship('Paciente', backref='psicologo', lazy='dynamic')

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

