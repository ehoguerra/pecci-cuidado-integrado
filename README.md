# Pecci Cuidado Integrado

Sistema de gerenciamento completo para clínicas de psicologia, desenvolvido com Flask e focado na gestão de pacientes, consultas e evoluções clínicas.

## 🎯 Sobre o Projeto

O **Pecci Cuidado Integrado** é uma plataforma web moderna e segura que oferece:

- **Gerenciamento de Psicólogos**: Cadastro e administração de profissionais
- **Dashboard Personalizado**: Interface moderna para psicólogos
- **Gestão de Pacientes**: Cadastro completo com dados criptografados
- **Evoluções Clínicas**: Sistema seguro para registros de sessões
- **Blog Integrado**: Plataforma para conteúdo educativo
- **Sistema Administrativo**: Painel completo para administradores
- **Responsividade Total**: Interface adaptada para todos os dispositivos

## 🚀 Características Principais

### ✅ Segurança
- Criptografia automática de dados sensíveis
- Autenticação por nível de usuário
- Conformidade com LGPD
- Hash seguro de senhas com bcrypt

### ✅ Interface Moderna
- Design responsivo com Bootstrap 5
- Paleta de cores verde profissional
- Animações suaves e interativas
- Experiência otimizada para mobile

### ✅ Funcionalidades Avançadas
- Busca em tempo real
- Validação inteligente de formulários
- Sistema de notificações
- Atalhos de teclado para produtividade

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask 3.1.1** - Framework web principal
- **SQLAlchemy 2.0.41** - ORM para banco de dados
- **Flask-Login 0.6.3** - Sistema de autenticação
- **Flask-Migrate 4.1.0** - Migrações de banco
- **cryptography 45.0.5** - Criptografia de dados
- **bcrypt 4.3.0** - Hash de senhas

### Frontend
- **Bootstrap 5.3.0** - Framework CSS
- **Bootstrap Icons** - Iconografia
- **JavaScript ES6+** - Interatividade
- **CSS3** - Estilos customizados

### Banco de Dados
- **PostgreSQL** (produção)
- **SQLite** (desenvolvimento)
- Suporte para **MySQL**

## 📦 Instalação

### Pré-requisitos
- Python 3.8+
- pip (gerenciador de pacotes Python)
- PostgreSQL (para produção)

### 1. Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/pecci-cuidado-integrado.git
cd pecci-cuidado-integrado
```

### 2. Criar Ambiente Virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:

```env
# Configurações da Aplicação
DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=sqlite:///agendamento.db

# Configurações do Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=sua-senha-admin
ADMIN_EMAIL=admin@exemplo.com

# Configurações de Criptografia
ENCRYPTION_KEY=sua-chave-de-criptografia

# Configurações de Email (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-app
```

### 5. Inicializar Banco de Dados
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Executar a Aplicação
```bash
python app.py
```

A aplicação estará disponível em `http://localhost:8000`

## 🔐 Segurança e Configuração

### Gerar Chave de Criptografia
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Gerar Secret Key
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 📱 Estrutura da Aplicação

```
pecci-cuidado-integrado/
├── app.py                      # Aplicação principal
├── config.py                   # Configurações
├── db.py                       # Configuração do banco
├── requirements.txt            # Dependências
├── controllers/                # Controladores MVC
│   ├── appointments_controller.py
│   ├── blog_controller.py
│   ├── doctors_controller.py
│   ├── slot_controller.py
│   └── user_controller.py
├── models/                     # Modelos de dados
│   ├── appointments.py
│   ├── blog_model.py
│   ├── doctors.py
│   ├── slots.py
│   └── user.py
├── dashboard_psi/              # Dashboard dos psicólogos
│   ├── models.py
│   ├── routes.py
│   ├── forms.py
│   ├── utils.py
│   ├── templates/
│   └── static/
├── templates/                  # Templates HTML
└── static/                     # Arquivos estáticos
    ├── css/
    ├── js/
    └── uploads/
```

## 🌐 Rotas Principais

### Públicas
- `/` - Página inicial
- `/blog` - Blog com artigos
- `/doctors` - Lista de psicólogos

### Psicólogos
- `/p/login` - Login de psicólogos
- `/dashboard-psicologia/` - Dashboard principal
- `/dashboard-psicologia/pacientes` - Gestão de pacientes
- `/dashboard-psicologia/agenda` - Agenda de consultas

### Administrativas
- `/admin/login` - Login administrativo
- `/admin/dashboard` - Painel administrativo
- `/admin/create-doctor` - Cadastrar psicólogo
- `/admin/edit-doctor/<id>` - Editar psicólogo

## 🎨 Design e UX

### Paleta de Cores
- **Verde Primário**: `#28a745` - Elementos principais
- **Verde Claro**: `#d4edda` - Fundos suaves
- **Verde Médio**: `#c3e6cb` - Gradientes
- **Verde Escuro**: `#155724` - Textos importantes

### Características do Design
- Interface responsiva e moderna
- Gradientes suaves para profundidade
- Animações para melhor experiência
- Iconografia consistente
- Foco na acessibilidade

## 📊 Funcionalidades do Dashboard

### Para Psicólogos
- Gestão completa de pacientes
- Registro de evoluções clínicas
- Agenda de consultas
- Estatísticas personalizadas
- Sistema de busca avançada

### Para Administradores
- Gerenciamento de psicólogos
- Estatísticas globais do sistema
- Controle de acesso
- Backup e segurança
- Monitoramento de atividades

## 🔍 Módulo de Integração

O projeto inclui um módulo independente (`dashboard_psi_module/`) que pode ser integrado a outras aplicações Flask:

- Blueprint modular
- Instalação simples
- Configuração flexível
- Documentação completa

## 🧪 Testes

### Executar Testes
```bash
python -m pytest tests/
```

### Teste de Criptografia
```bash
python test_encryption.py
```

## 📝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🤝 Suporte

Para dúvidas, sugestões ou problemas:

- **Email**: contato@peccicuidadointegrado.com.br
- **LinkedIn**: [Artur Guerra](https://www.linkedin.com/in/artur-guerra-dev/)
- **Issues**: Use a aba Issues do GitHub

## 🎯 Roadmap

### Próximas Funcionalidades
- [ ] Sistema de notificações push
- [ ] Integração com calendário externo
- [ ] Relatórios avançados em PDF
- [ ] API REST completa
- [ ] Aplicativo mobile
- [ ] Sistema de backup automático

## ⚖️ Conformidade

O sistema foi desenvolvido seguindo:
- **LGPD** - Lei Geral de Proteção de Dados
- **CFP** - Resolução do Conselho Federal de Psicologia
- **Boas práticas** de segurança em aplicações web

---

**Desenvolvido com ❤️ para profissionais da saúde mental**

**Versão**: 1.0.0  
**Última atualização**: 2025
