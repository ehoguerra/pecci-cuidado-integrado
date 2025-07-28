"""
Dashboard Psicologia - Módulo para integração
Módulo Flask para gerenciamento de pacientes e evoluções clínicas
"""

from flask import Blueprint

bp = Blueprint('dashboard_psi', __name__,
               url_prefix='/dashboard-psicologia',
               template_folder='templates',
               static_folder='static',
               static_url_path='/dashboard-psi/static')

from . import routes
