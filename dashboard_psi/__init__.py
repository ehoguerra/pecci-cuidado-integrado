"""
Dashboard Psicologia - Módulo para integração
Módulo Flask para gerenciamento de pacientes e evoluções clínicas
"""

from flask import Blueprint
from .utils import nl2br

bp = Blueprint('dashboard_psi', __name__,
               url_prefix='/dashboard-psicologia',
               template_folder='templates',
               static_folder='static',
               static_url_path='/dashboard-psi/static')

# Registrar filtros personalizados
bp.add_app_template_filter(nl2br, 'nl2br')

from . import routes
