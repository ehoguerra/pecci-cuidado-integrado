# Dashboard Psicologia - Módulo de Integração

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
