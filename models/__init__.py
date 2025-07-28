# models/__init__.py
"""
Pacote de modelos do sistema de agendamento de consultas
"""

from .user import User
from .doctors import Doctors
from .appointments import Appointments
from .slots import Slots
try:
    from .blog_model import BlogModel
except ImportError:
    pass

__all__ = ['User', 'Doctors', 'Appointments', 'Slots', 'BlogModel']
