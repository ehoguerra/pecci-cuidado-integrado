# app/__init__.py

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


login_manager.login_message = 'Por favor, faça o login para acessar esta página.'
login_manager.login_message_category = 'info' # Categoria para o sistema de flash messages


# 3. Definição da Fábrica de Aplicação
def create_app(config_class=Config):
    app = Flask(__name__)
    

    app.config.from_object(config_class)
    

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)
    

    return app