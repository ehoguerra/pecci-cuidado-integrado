# Exemplo de integração no app principal

# 1. No arquivo app/__init__.py:
def create_app():
    app = Flask(__name__)
    # ... configurações existentes ...
    
    # Registrar blueprint do dashboard
    from app.dashboard_psi import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    return app

# 2. Adicionar ao modelo User (app/models.py):
class User(UserMixin, db.Model):
    # ... campos existentes ...
    
    # Campos para psicólogos
    crp = db.Column(db.String(20), nullable=True)
    especialidades = db.Column(db.Text, nullable=True)
    
    # Relacionamento com pacientes
    pacientes = db.relationship('Paciente', backref='psicologo', lazy='dynamic')
    
    def is_psicologo(self):
        return self.crp is not None and self.crp.strip() != ''

# 3. No template base (templates/base.html):
{% if current_user.is_authenticated and current_user.is_psicologo() %}
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('dashboard_psi.dashboard') }}">
        Dashboard Psicologia
    </a>
</li>
{% endif %}

# 4. Migração do banco:
flask db migrate -m "Add psicologia dashboard"
flask db upgrade
