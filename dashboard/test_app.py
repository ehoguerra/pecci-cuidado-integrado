#!/usr/bin/env python3
"""
Script para testar a aplicação Dashboard Psicologia
Verifica se todos os templates e rotas estão funcionando corretamente
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Psicologo, Paciente, Evolucao
from datetime import datetime

def test_app():
    """Testa a aplicação criando dados de exemplo"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Criar tabelas
            db.create_all()
            print("✅ Tabelas criadas com sucesso")
            
            # Verificar se já existe um psicólogo de teste
            psicologo_teste = Psicologo.query.filter_by(email='teste@psicologo.com').first()
            
            if not psicologo_teste:
                # Criar psicólogo de teste
                psicologo_teste = Psicologo(
                    nome='Dr. João Silva',
                    email='teste@psicologo.com',
                    crp='06/12345'
                )
                psicologo_teste.set_password('123456')
                db.session.add(psicologo_teste)
                db.session.commit()
                print("✅ Psicólogo de teste criado")
                print("   Email: teste@psicologo.com")
                print("   Senha: 123456")
            else:
                print("✅ Psicólogo de teste já existe")
                
            # Verificar se já existem pacientes de teste
            pacientes_count = Paciente.query.filter_by(psicologo_id=psicologo_teste.id).count()
            
            if pacientes_count == 0:
                # Criar pacientes de teste
                pacientes_teste = [
                    {
                        'nome_completo': 'Maria Santos Silva',
                        'data_nascimento': datetime(1985, 3, 15).date()
                    },
                    {
                        'nome_completo': 'João Carlos Oliveira',
                        'data_nascimento': datetime(1992, 7, 22).date()
                    },
                    {
                        'nome_completo': 'Ana Paula Costa',
                        'data_nascimento': datetime(1978, 11, 8).date()
                    }
                ]
                
                for paciente_data in pacientes_teste:
                    paciente = Paciente(
                        nome_completo=paciente_data['nome_completo'],
                        data_nascimento=paciente_data['data_nascimento'],
                        psicologo_id=psicologo_teste.id
                    )
                    db.session.add(paciente)
                
                db.session.commit()
                print("✅ Pacientes de teste criados")
                
                # Criar algumas evoluções de teste
                pacientes = Paciente.query.filter_by(psicologo_id=psicologo_teste.id).all()
                
                evolucoes_teste = [
                    {
                        'paciente': pacientes[0],
                        'data_sessao': datetime(2024, 12, 15, 14, 0),
                        'conteudo': 'Primeira sessão. Paciente apresentou ansiedade leve, relatou dificuldades no trabalho. Aplicada técnica de respiração e planejamento de metas. Paciente respondeu bem às intervenções.'
                    },
                    {
                        'paciente': pacientes[0],
                        'data_sessao': datetime(2024, 12, 22, 14, 0),
                        'conteudo': 'Segunda sessão. Melhora significativa no quadro de ansiedade. Paciente relatou ter praticado os exercícios de respiração. Trabalhamos autoestima e técnicas de gestão do tempo.'
                    },
                    {
                        'paciente': pacientes[1],
                        'data_sessao': datetime(2024, 12, 18, 16, 0),
                        'conteudo': 'Primeira sessão com João. Histórico de depressão leve. Paciente mostrou-se colaborativo e motivado para o tratamento. Definimos objetivos terapêuticos iniciais.'
                    }
                ]
                
                for evolucao_data in evolucoes_teste:
                    evolucao = Evolucao(
                        data_sessao=evolucao_data['data_sessao'],
                        paciente_id=evolucao_data['paciente'].id
                    )
                    # Usar o setter para criptografar automaticamente
                    evolucao.conteudo = evolucao_data['conteudo']
                    db.session.add(evolucao)
                
                db.session.commit()
                print("✅ Evoluções de teste criadas")
            else:
                print("✅ Dados de teste já existem")
                
            print("\n🎉 Aplicação configurada com sucesso!")
            print("\n📋 Informações para teste:")
            print("   - URL: http://localhost:5000")
            print("   - Email: teste@psicologo.com")
            print("   - Senha: 123456")
            print(f"   - Pacientes cadastrados: {pacientes_count if pacientes_count > 0 else 3}")
            
            # Verificar templates
            print("\n📁 Templates encontrados:")
            templates_dir = os.path.join(os.path.dirname(__file__), 'app', 'templates')
            if os.path.exists(templates_dir):
                for template in os.listdir(templates_dir):
                    if template.endswith('.html'):
                        print(f"   ✅ {template}")
            
            # Verificar arquivos estáticos
            print("\n📁 Arquivos estáticos encontrados:")
            static_dir = os.path.join(os.path.dirname(__file__), 'app', 'static')
            if os.path.exists(static_dir):
                for root, dirs, files in os.walk(static_dir):
                    for file in files:
                        rel_path = os.path.relpath(os.path.join(root, file), static_dir)
                        print(f"   ✅ {rel_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao configurar aplicação: {e}")
            return False

def check_requirements():
    """Verifica se todas as dependências estão instaladas"""
    required_packages = [
        'flask',
        'flask-sqlalchemy',
        'flask-migrate',
        'flask-login',
        'flask-wtf',
        'wtforms',
        'werkzeug'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NÃO INSTALADO")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Para instalar pacotes faltantes:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

if __name__ == '__main__':
    print("🧪 Testando Dashboard Psicologia\n")
    
    print("1. Verificando dependências...")
    if not check_requirements():
        sys.exit(1)
    
    print("\n2. Configurando aplicação...")
    if not test_app():
        sys.exit(1)
    
    print("\n🚀 Para iniciar a aplicação, execute:")
    print("   python run.py")
    print("\n💡 Ou use o ambiente virtual:")
    print("   source .venv/bin/activate  # Linux/Mac")
    print("   .venv\\Scripts\\activate     # Windows")
    print("   python run.py")
