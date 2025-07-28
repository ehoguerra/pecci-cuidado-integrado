from app import create_app, db
from app.models import Psicologo, Paciente, Evolucao

# Chama a fábrica para criar a instância da aplicação
app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Psicologo': Psicologo, 'Paciente': Paciente, 'Evolucao': Evolucao}

if __name__ == '__main__':
    app.run(debug=True)