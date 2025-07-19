#!/usr/bin/env python3
"""
Script para testar a criação das tabelas do banco de dados
"""

from flask import Flask
from db import db
# Importar todos os modelos para que o SQLAlchemy os reconheça
from models.user import User
from models.doctors import Doctors
from models.appointments import Appointments
from models.slots import Slots

def create_tables():
    """Cria as tabelas no banco de dados"""
    
    # Configurar a aplicação Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123911ar@localhost/consultas'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Inicializar o SQLAlchemy
    db.init_app(app)
    
    # Criar as tabelas dentro do contexto da aplicação
    with app.app_context():
        try:
            print("Conectando ao banco de dados...")
            
            # Deletar todas as tabelas (cuidado: isso remove todos os dados!)
            print("Removendo tabelas existentes...")
            db.drop_all()
            
            # Criar todas as tabelas
            print("Criando tabelas...")
            db.create_all()
            
            print("✅ Tabelas criadas com sucesso!")
            
            # Verificar se as tabelas foram criadas
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("\n📋 Tabelas encontradas no banco:")
            for table in tables:
                print(f"  - {table}")
            
            # Verificar a estrutura de cada tabela
            expected_tables = ['users', 'doctors', 'appointments', 'slots']
            for table_name in expected_tables:
                if table_name in tables:
                    print(f"\n📊 Estrutura da tabela '{table_name}':")
                    columns = inspector.get_columns(table_name)
                    for column in columns:
                        print(f"  - {column['name']}: {column['type']}")
                else:
                    print(f"❌ Tabela '{table_name}' não foi criada!")
            
        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    create_tables()
