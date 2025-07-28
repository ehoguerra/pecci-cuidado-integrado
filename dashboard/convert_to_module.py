#!/usr/bin/env python3
"""
Script para converter o Dashboard Psicologia em um módulo integrável
Prepara os arquivos para integração em um site Flask existente
"""

import os
import shutil
import sys
from pathlib import Path

def create_module_structure():
    """Cria a estrutura de módulo para integração"""
    
    base_dir = Path(__file__).parent
    module_dir = base_dir / "dashboard_psi_module"
    
    print("🏗️  Criando estrutura do módulo...")
    
    # Criar diretórios
    dirs_to_create = [
        module_dir,
        module_dir / "templates" / "dashboard_psi",
        module_dir / "templates" / "dashboard_psi" / "pacientes",
        module_dir / "templates" / "dashboard_psi" / "evolucoes",
        module_dir / "static" / "css",
        module_dir / "static" / "js",
        module_dir / "static" / "img"
    ]
    
    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"   📁 {dir_path.relative_to(base_dir)}")
    
    return module_dir

def copy_and_adapt_files(module_dir):
    """Copia e adapta os arquivos para o módulo (sem alterar originais)"""
    
    base_dir = Path(__file__).parent
    
    print("\n📋 Copiando arquivos (mantendo originais intactos)...")
    
    # 1. Copiar arquivos Python principais (CÓPIAS INDEPENDENTES)
    python_files = ['models.py', 'forms.py', 'utils.py']
    for file_name in python_files:
        src = base_dir / "app" / file_name
        dst = module_dir / file_name
        if src.exists():
            # Criar cópia independente
            shutil.copy2(src, dst)
            print(f"   ✅ {file_name} (cópia independente)")
        else:
            print(f"   ⚠️  {file_name} não encontrado")
    
    # 2. Copiar templates para subdiretório (CÓPIAS INDEPENDENTES)
    templates_src = base_dir / "app" / "templates"
    templates_dst = module_dir / "templates" / "dashboard_psi"
    
    if templates_src.exists():
        for template_file in templates_src.glob("*.html"):
            # Criar cópia independente
            shutil.copy2(template_file, templates_dst / template_file.name)
            print(f"   ✅ templates/{template_file.name} (cópia independente)")
    else:
        print("   ⚠️  Diretório templates não encontrado")
    
    # 3. Copiar arquivos estáticos (CÓPIAS INDEPENDENTES)
    static_src = base_dir / "app" / "static"
    static_dst = module_dir / "static"
    
    if static_src.exists():
        for static_dir in ['css', 'js', 'img']:
            src_dir = static_src / static_dir
            dst_dir = static_dst / static_dir
            if src_dir.exists():
                # Criar diretório se não existir
                dst_dir.mkdir(exist_ok=True)
                for file in src_dir.glob("*"):
                    if file.is_file():
                        # Criar cópia independente
                        shutil.copy2(file, dst_dir / file.name)
                        print(f"   ✅ static/{static_dir}/{file.name} (cópia independente)")
    else:
        print("   ⚠️  Diretório static não encontrado")
    
    # 4. Copiar arquivo de configuração como referência
    config_src = base_dir / "config.py"
    if config_src.exists():
        config_dst = module_dir / "config_reference.py"
        shutil.copy2(config_src, config_dst)
        print(f"   ✅ config_reference.py (para referência)")
    
    print(f"\n📂 Todos os arquivos foram COPIADOS para: {module_dir}")
    print("🔒 Os arquivos originais permanecem INTACTOS")

def create_module_init(module_dir):
    """Cria o arquivo __init__.py do módulo"""
    
    init_content = '''"""
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
'''
    
    init_file = module_dir / "__init__.py"
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write(init_content)
    
    print("   ✅ __init__.py criado")

def create_adapted_routes(module_dir):
    """Cria arquivo de rotas adaptado para integração"""
    
    routes_content = '''# dashboard_psi/routes.py
"""
Rotas do Dashboard Psicologia adaptadas para integração
"""

from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from . import bp
from .models import Paciente, Evolucao
from .forms import PacienteForm, EvolucaoForm
from .utils import encrypt_data, decrypt_data
from app import db
from functools import wraps

def psicologo_required(f):
    """Decorator para verificar se o usuário é psicólogo"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        # Verificar se é psicólogo (adapte conforme seu modelo User)
        if not hasattr(current_user, 'crp') or not current_user.crp:
            flash('Acesso restrito a psicólogos cadastrados.', 'warning')
            abort(403)
            
        return f(*args, **kwargs)
    return decorated_function

# --- Dashboard Principal ---
@bp.route('/')
@psicologo_required
def dashboard():
    """Dashboard principal do módulo"""
    # Buscar pacientes do psicólogo atual
    pacientes = Paciente.query.filter_by(psicologo_id=current_user.id).all()
    
    # Estatísticas
    total_pacientes = len(pacientes)
    total_evolucoes = sum(len(p.evolucoes) for p in pacientes)
    
    # Últimas evoluções
    ultimas_evolucoes = (Evolucao.query
                        .join(Paciente)
                        .filter(Paciente.psicologo_id == current_user.id)
                        .order_by(Evolucao.data_sessao.desc())
                        .limit(5)
                        .all())
    
    return render_template('dashboard_psi/dashboard.html',
                         title='Dashboard Psicologia',
                         pacientes=pacientes,
                         total_pacientes=total_pacientes,
                         total_evolucoes=total_evolucoes,
                         ultimas_evolucoes=ultimas_evolucoes)

# --- Rotas de Pacientes ---
@bp.route('/pacientes')
@psicologo_required
def listar_pacientes():
    """Lista todos os pacientes do psicólogo"""
    search = request.args.get('search', '')
    
    query = Paciente.query.filter_by(psicologo_id=current_user.id)
    
    if search:
        query = query.filter(Paciente.nome_completo.contains(search))
    
    pacientes = query.order_by(Paciente.nome_completo).all()
    
    return render_template('dashboard_psi/listar_pacientes.html',
                         title='Pacientes',
                         pacientes=pacientes,
                         search=search)

@bp.route('/pacientes/novo', methods=['GET', 'POST'])
@psicologo_required
def novo_paciente():
    """Cadastrar novo paciente"""
    form = PacienteForm()
    
    if form.validate_on_submit():
        paciente = Paciente(
            nome_completo=form.nome_completo.data,
            data_nascimento=form.data_nascimento.data,
            telefone=form.telefone.data,
            email=form.email.data,
            endereco=form.endereco.data,
            profissao=form.profissao.data,
            estado_civil=form.estado_civil.data,
            contato_emergencia=form.contato_emergencia.data,
            observacoes=form.observacoes.data,
            psicologo_id=current_user.id
        )
        
        db.session.add(paciente)
        db.session.commit()
        
        flash(f'Paciente {paciente.nome_completo} cadastrado com sucesso!', 'success')
        return redirect(url_for('dashboard_psi.perfil_paciente', id=paciente.id))
    
    return render_template('dashboard_psi/form_paciente.html',
                         title='Novo Paciente',
                         form=form)

@bp.route('/pacientes/<int:id>')
@psicologo_required
def perfil_paciente(id):
    """Perfil do paciente com histórico de evoluções"""
    paciente = Paciente.query.filter_by(
        id=id, 
        psicologo_id=current_user.id
    ).first_or_404()
    
    # Buscar evoluções com paginação
    page = request.args.get('page', 1, type=int)
    evolucoes = (Evolucao.query
                .filter_by(paciente_id=paciente.id)
                .order_by(Evolucao.data_sessao.desc())
                .paginate(
                    page=page, 
                    per_page=10, 
                    error_out=False
                ))
    
    return render_template('dashboard_psi/perfil_paciente.html',
                         title=f'Paciente: {paciente.nome_completo}',
                         paciente=paciente,
                         evolucoes=evolucoes)

# --- Rotas de Evoluções ---
@bp.route('/pacientes/<int:paciente_id>/evolucoes/nova', methods=['GET', 'POST'])
@psicologo_required
def nova_evolucao(paciente_id):
    """Criar nova evolução para o paciente"""
    paciente = Paciente.query.filter_by(
        id=paciente_id,
        psicologo_id=current_user.id
    ).first_or_404()
    
    form = EvolucaoForm()
    
    if form.validate_on_submit():
        evolucao = Evolucao(
            data_sessao=form.data_sessao.data,
            paciente_id=paciente.id
        )
        # Usar criptografia automática
        evolucao.conteudo = form.conteudo.data
        
        db.session.add(evolucao)
        db.session.commit()
        
        flash('Evolução registrada com sucesso!', 'success')
        return redirect(url_for('dashboard_psi.perfil_paciente', id=paciente.id))
    
    # Pré-preencher data de hoje
    if not form.data_sessao.data:
        from datetime import datetime
        form.data_sessao.data = datetime.now()
    
    return render_template('dashboard_psi/form_evolucao.html',
                         title='Nova Evolução',
                         form=form,
                         paciente=paciente)

@bp.route('/evolucoes/<int:id>/editar', methods=['GET', 'POST'])
@psicologo_required
def editar_evolucao(id):
    """Editar evolução existente"""
    evolucao = Evolucao.query.join(Paciente).filter(
        Evolucao.id == id,
        Paciente.psicologo_id == current_user.id
    ).first_or_404()
    
    form = EvolucaoForm(obj=evolucao)
    
    if form.validate_on_submit():
        evolucao.data_sessao = form.data_sessao.data
        evolucao.conteudo = form.conteudo.data  # Criptografia automática
        
        db.session.commit()
        
        flash('Evolução atualizada com sucesso!', 'success')
        return redirect(url_for('dashboard_psi.perfil_paciente', id=evolucao.paciente_id))
    
    # Pré-preencher formulário (descriptografia automática)
    form.conteudo.data = evolucao.conteudo
    
    return render_template('dashboard_psi/form_evolucao.html',
                         title='Editar Evolução',
                         form=form,
                         paciente=evolucao.paciente,
                         evolucao=evolucao)

# --- API Routes (opcional) ---
@bp.route('/api/pacientes/search')
@psicologo_required
def api_search_pacientes():
    """API para busca de pacientes (AJAX)"""
    query = request.args.get('q', '')
    
    if len(query) < 2:
        return jsonify([])
    
    pacientes = (Paciente.query
                .filter_by(psicologo_id=current_user.id)
                .filter(Paciente.nome_completo.contains(query))
                .limit(10)
                .all())
    
    results = [
        {
            'id': p.id,
            'nome': p.nome_completo,
            'idade': p.idade,
            'total_evolucoes': len(p.evolucoes)
        }
        for p in pacientes
    ]
    
    return jsonify(results)
'''
    
    routes_file = module_dir / "routes.py"
    with open(routes_file, 'w', encoding='utf-8') as f:
        f.write(routes_content)
    
    print("   ✅ routes.py adaptado criado")

def create_integration_example(module_dir):
    """Cria exemplo de integração no app principal"""
    
    integration_example = '''# Exemplo de integração no app principal

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
'''
    
    example_file = module_dir / "INTEGRATION_EXAMPLE.py"
    with open(example_file, 'w', encoding='utf-8') as f:
        f.write(integration_example)
    
    print("   ✅ INTEGRATION_EXAMPLE.py criado")

def create_requirements(module_dir):
    """Cria arquivo de dependências do módulo"""
    
    requirements = '''# Dependências do Dashboard Psicologia

# Já devem estar instaladas no projeto principal:
Flask>=2.0.0
Flask-SQLAlchemy>=3.0.0
Flask-Login>=0.6.0
Flask-WTF>=1.1.0
WTForms>=3.0.0

# Específicas do dashboard:
cryptography>=41.0.0  # Para criptografia das evoluções
'''
    
    req_file = module_dir / "requirements.txt"
    with open(req_file, 'w', encoding='utf-8') as f:
        f.write(requirements)
    
    print("   ✅ requirements.txt criado")

def create_module_readme(module_dir):
    """Cria documentação do módulo"""
    
    readme_content = '''# Dashboard Psicologia - Módulo de Integração

Este é um módulo Flask independente para gerenciamento de pacientes e evoluções clínicas, desenvolvido para ser integrado em aplicações Flask existentes.

## 🎯 Características

- **Modular**: Blueprint independente com namespace próprio
- **Seguro**: Criptografia automática dos dados sensíveis
- **Responsivo**: Interface moderna com Bootstrap 5
- **Compatível**: Integra-se facilmente com sistemas Flask existentes

## 📦 Estrutura do Módulo

```
dashboard_psi/
├── __init__.py              # Configuração do Blueprint
├── routes.py                # Rotas do dashboard
├── models.py                # Modelos de dados
├── forms.py                 # Formulários WTF
├── utils.py                 # Utilitários (criptografia)
├── templates/
│   └── dashboard_psi/       # Templates com namespace
├── static/
│   ├── css/                 # Estilos personalizados
│   └── js/                  # Scripts JavaScript
└── requirements.txt         # Dependências
```

## 🚀 Instalação

### 1. Copiar Módulo

```bash
# Copie a pasta para seu projeto
cp -r dashboard_psi_module/ /caminho/para/seu/projeto/app/dashboard_psi/
```

### 2. Instalar Dependências

```bash
pip install cryptography>=41.0.0
```

### 3. Registrar Blueprint

No arquivo `app/__init__.py`:

```python
def create_app():
    app = Flask(__name__)
    # ... suas configurações ...
    
    # Registrar dashboard psicologia
    from app.dashboard_psi import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    return app
```

### 4. Configurar Modelo User

Adicione campos ao seu modelo User existente:

```python
class User(UserMixin, db.Model):
    # ... campos existentes ...
    
    # Campos para psicólogos
    crp = db.Column(db.String(20), nullable=True)
    especialidades = db.Column(db.Text, nullable=True)
    
    def is_psicologo(self):
        return self.crp is not None and self.crp.strip() != ''
```

### 5. Configurar Criptografia

No arquivo `.env`:

```env
ENCRYPTION_KEY=sua_chave_de_criptografia_aqui
```

Para gerar uma chave:

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 6. Executar Migrações

```bash
flask db migrate -m "Add dashboard psicologia"
flask db upgrade
```

## 🌐 URLs Disponíveis

- `/dashboard-psicologia/` - Dashboard principal
- `/dashboard-psicologia/pacientes` - Lista de pacientes
- `/dashboard-psicologia/pacientes/novo` - Cadastrar paciente
- `/dashboard-psicologia/pacientes/<id>` - Perfil do paciente
- `/dashboard-psicologia/pacientes/<id>/evolucoes/nova` - Nova evolução

## 🔐 Segurança

### Controle de Acesso

O módulo usa o decorator `@psicologo_required` que:

1. Verifica se o usuário está autenticado
2. Confirma se possui CRP (é psicólogo)
3. Bloqueia acesso caso contrário

### Criptografia

- Evoluções são automaticamente criptografadas
- Chave configurável via variável de ambiente
- Descriptografia transparente na leitura

## 🎨 Personalização

### Templates

Os templates estão em `templates/dashboard_psi/` e podem ser customizados:

- `dashboard.html` - Página principal
- `form_paciente.html` - Formulário de pacientes
- `perfil_paciente.html` - Perfil e histórico
- `form_evolucao.html` - Formulário de evoluções

### Estilos

CSS personalizado em `static/css/styles.css` com:

- Variáveis CSS para cores
- Tema verde profissional
- Responsividade mobile
- Animações suaves

## 🧪 Testes

Para testar a integração:

```python
# Criar usuário psicólogo
user = User(email='psi@teste.com', crp='06/12345')
user.set_password('senha123')
db.session.add(user)
db.session.commit()

# Acessar: /dashboard-psicologia/
```

## ⚙️ Configurações Opcionais

### Menu de Navegação

Adicione ao template base do seu site:

```html
{% if current_user.is_authenticated and current_user.is_psicologo() %}
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('dashboard_psi.dashboard') }}">
        Dashboard Psicologia
    </a>
</li>
{% endif %}
```

### Permissões Avançadas

Para controle mais granular, modifique o decorator em `routes.py`:

```python
def psicologo_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Suas validações personalizadas aqui
        return f(*args, **kwargs)
    return decorated_function
```

## 🔧 Troubleshooting

### Erro: Template não encontrado
- Verifique se o módulo está registrado corretamente
- Confirme se `template_folder='templates'` está no Blueprint

### Erro: Static files não carregam
- Verifique se `static_folder='static'` está no Blueprint
- Confirme o `static_url_path='/dashboard-psi/static'`

### Erro: Banco de dados
- Execute `flask db migrate` e `flask db upgrade`
- Verifique se as tabelas foram criadas

### Erro: Criptografia
- Configure a variável `ENCRYPTION_KEY`
- Instale `cryptography>=41.0.0`

## 📞 Suporte

Este módulo foi desenvolvido para ser:
- ✅ Independente da aplicação principal
- ✅ Fácil de integrar e remover
- ✅ Compatível com diferentes estruturas Flask
- ✅ Seguro e conforme com LGPD

Para dúvidas ou customizações, consulte os arquivos:
- `INTEGRATION_EXAMPLE.py` - Exemplos práticos
- `routes.py` - Lógica das rotas
- `models.py` - Estrutura dos dados

---
**Dashboard Psicologia** - Versão modular para integração
'''
    
    readme_file = module_dir / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("   ✅ README.md criado")

def update_template_paths(module_dir):
    """Atualiza os paths dos templates para o namespace do módulo (apenas nas cópias)"""
    
    print("\n🔧 Atualizando paths nos templates (apenas nas cópias)...")
    
    templates_dir = module_dir / "templates" / "dashboard_psi"
    
    # Mapeamento de substituições para integração
    replacements = {
        "url_for('main.dashboard')": "url_for('dashboard_psi.dashboard')",
        "url_for('dashboard')": "url_for('dashboard_psi.dashboard')",
        "url_for('listar_pacientes')": "url_for('dashboard_psi.listar_pacientes')",
        "url_for('novo_paciente')": "url_for('dashboard_psi.novo_paciente')",
        "url_for('perfil_paciente'": "url_for('dashboard_psi.perfil_paciente'",
        "url_for('nova_evolucao'": "url_for('dashboard_psi.nova_evolucao'",
        "url_for('editar_evolucao'": "url_for('dashboard_psi.editar_evolucao'",
        "url_for('main.login')": "url_for('auth.login')",  # Assumindo blueprint auth
        "url_for('login')": "url_for('auth.login')",
        "url_for('logout')": "url_for('auth.logout')",
        "{{ url_for('static'": "{{ url_for('dashboard_psi.static'",
        "'css/styles.css'": "'css/styles.css'",  # Manter como está dentro do blueprint
        "'js/dashboard.js'": "'js/dashboard.js'"   # Manter como está dentro do blueprint
    }
    
    if not templates_dir.exists():
        print("   ⚠️  Diretório de templates não encontrado")
        return
    
    for template_file in templates_dir.glob("*.html"):
        if template_file.is_file():
            try:
                content = template_file.read_text(encoding='utf-8')
                
                # Aplicar substituições
                original_content = content
                for old, new in replacements.items():
                    content = content.replace(old, new)
                
                # Salvar apenas se houve mudanças
                if content != original_content:
                    template_file.write_text(content, encoding='utf-8')
                    print(f"   ✅ {template_file.name} atualizado")
                else:
                    print(f"   📄 {template_file.name} (sem alterações necessárias)")
                    
            except Exception as e:
                print(f"   ❌ Erro ao processar {template_file.name}: {e}")
    
    print("🔒 Templates originais permanecem intactos!")

def main():
    """Função principal do script"""
    
    print("🔄 Criando módulo Dashboard Psicologia para integração")
    print("🔒 Mantendo aplicação original INTACTA")
    print("=" * 60)
    
    try:
        # 1. Criar estrutura do módulo separado
        module_dir = create_module_structure()
        
        # 2. Copiar arquivos (mantendo originais intactos)
        copy_and_adapt_files(module_dir)
        
        # 3. Criar arquivos específicos do módulo
        create_module_init(module_dir)
        create_adapted_routes(module_dir)
        create_integration_example(module_dir)
        create_requirements(module_dir)
        
        # 4. Atualizar templates nas cópias
        update_template_paths(module_dir)
        
        # 5. Criar README do módulo
        create_module_readme(module_dir)
        
        print("\n" + "=" * 60)
        print("✅ MÓDULO CRIADO COM SUCESSO!")
        print("🔒 Aplicação original permanece INTACTA")
        print(f"\n📁 Localização do módulo: {module_dir}")
        
        print("\n� Conteúdo do módulo:")
        print("   ├── __init__.py              (Blueprint configuration)")
        print("   ├── routes.py                (Rotas adaptadas)")
        print("   ├── models.py                (Modelos copiados)")
        print("   ├── forms.py                 (Formulários copiados)")
        print("   ├── utils.py                 (Utilitários copiados)")
        print("   ├── requirements.txt         (Dependências)")
        print("   ├── INTEGRATION_EXAMPLE.py   (Guia de integração)")
        print("   ├── README.md                (Documentação)")
        print("   ├── config_reference.py      (Config para referência)")
        print("   ├── templates/")
        print("   │   └── dashboard_psi/       (Templates adaptados)")
        print("   └── static/")
        print("       ├── css/                 (Estilos copiados)")
        print("       ├── js/                  (Scripts copiados)")
        print("       └── img/                 (Imagens copiadas)")
        
        print("\n📋 Como usar:")
        print("   1. Copie toda pasta 'dashboard_psi_module' para seu projeto")
        print("   2. Renomeie para 'dashboard_psi' dentro de app/")
        print("   3. Siga instruções em INTEGRATION_EXAMPLE.py")
        print("   4. Leia README.md para detalhes de integração")
        
        print("\n🌐 URLs que estarão disponíveis:")
        print("   /dashboard-psicologia/")
        print("   /dashboard-psicologia/pacientes")
        print("   /dashboard-psicologia/pacientes/novo")
        print("   /dashboard-psicologia/pacientes/<id>")
        print("   /dashboard-psicologia/pacientes/<id>/evolucoes/nova")
        
        print("\n💡 Vantagens desta abordagem:")
        print("   ✅ Aplicação original permanece funcional")
        print("   ✅ Módulo independente e reutilizável")
        print("   ✅ Fácil de integrar e remover")
        print("   ✅ Namespace próprio evita conflitos")
        print("   ✅ Pode ser versionado separadamente")
        
    except Exception as e:
        print(f"\n❌ Erro durante a criação: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
