from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, DateField, TextAreaField, BooleanField, SelectField, IntegerField, TimeField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange
from wtforms.widgets import TextArea

class PacienteForm(FlaskForm):
    nome_completo = StringField('Nome Completo', validators=[DataRequired(), Length(max=150)])
    data_nascimento = DateField('Data de Nascimento', format='%Y-%m-%d', validators=[Optional()])
    telefone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])
    endereco = StringField('Endereço', validators=[Optional(), Length(max=200)])
    profissao = StringField('Profissão', validators=[Optional(), Length(max=100)])
    estado_civil = SelectField('Estado Civil', 
                              choices=[
                                  ('', 'Selecione...'),
                                  ('solteiro', 'Solteiro(a)'),
                                  ('casado', 'Casado(a)'),
                                  ('separado', 'Separado(a)'),
                                  ('divorciado', 'Divorciado(a)'),
                                  ('viuvo', 'Viúvo(a)'),
                                  ('uniao_estavel', 'União Estável')
                              ],
                              validators=[Optional()])
    contato_emergencia = TextAreaField('Contato de Emergência', validators=[Optional(), Length(max=200)])
    observacoes = TextAreaField('Observações', validators=[Optional()])
    
    submit = SubmitField('Salvar Paciente')

class EvolucaoForm(FlaskForm):
    data_sessao = DateField('Data da Sessão', format='%Y-%m-%d', validators=[DataRequired()])
    tipo_sessao = SelectField('Tipo de Sessão',
                             choices=[
                                 ('individual', 'Individual'),
                                 ('grupo', 'Grupo'),
                                 ('casal', 'Casal'),
                                 ('familia', 'Família'),
                                 ('avaliacao', 'Avaliação')
                             ],
                             validators=[Optional()])
    duracao_minutos = IntegerField('Duração (minutos)', 
                                  validators=[Optional(), NumberRange(min=1, max=480)],
                                  default=50)
    conteudo = TextAreaField('Conteúdo da Evolução', 
                           validators=[DataRequired(), Length(max=5000)],
                           widget=TextArea(),
                           render_kw={"rows": 10, "placeholder": "Descreva a evolução da sessão..."})
    
    submit = SubmitField('Salvar Evolução')

class PesquisaForm(FlaskForm):
    termo = StringField('Pesquisar pacientes...', 
                       validators=[Optional(), Length(max=100)],
                       render_kw={"placeholder": "Digite o nome do paciente..."})
    submit = SubmitField('Pesquisar')

class PerfilForm(FlaskForm):
    name = StringField('Nome Completo', validators=[DataRequired(), Length(max=150)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    crm = StringField('CRP/CRM', validators=[Optional(), Length(max=20)])
    telefone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    endereco = StringField('Endereço', validators=[Optional(), Length(max=200)])
    especialidade = StringField('Especialidade', validators=[Optional(), Length(max=100)])
    bio = TextAreaField('Biografia/Apresentação', 
                       validators=[Optional(), Length(max=500)],
                       render_kw={"rows": 4, "placeholder": "Conte um pouco sobre sua experiência profissional..."})
    foto_perfil = FileField('Foto do Perfil', 
                           validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Apenas imagens são permitidas!')])
    
    submit = SubmitField('Atualizar Perfil')

class AlterarSenhaForm(FlaskForm):
    senha_atual = PasswordField('Senha Atual', validators=[DataRequired()])
    nova_senha = PasswordField('Nova Senha', 
                              validators=[DataRequired(), Length(min=6, max=20)])
    confirmar_senha = PasswordField('Confirmar Nova Senha',
                                   validators=[DataRequired(), 
                                             EqualTo('nova_senha', message='As senhas devem coincidir')])
    
    submit = SubmitField('Alterar Senha')

class AgendaForm(FlaskForm):
    paciente_id = SelectField('Paciente', 
                             validators=[DataRequired()],
                             choices=[])
    data_consulta = DateField('Data da Consulta', 
                             validators=[DataRequired()],
                             format='%Y-%m-%d')
    hora_consulta = TimeField('Horário', 
                             validators=[DataRequired()])
    compromissos = StringField('Tipo de Consulta',
                              validators=[Length(max=200)],
                              render_kw={"placeholder": "Ex: Consulta inicial, Terapia individual..."})
    local = StringField('Local',
                       validators=[Length(max=200)],
                       render_kw={"placeholder": "Ex: Consultório 1, Online..."})
    observacoes = TextAreaField('Observações',
                               validators=[Length(max=500)],
                               render_kw={"rows": 3, "placeholder": "Observações sobre a consulta..."})
    status = SelectField('Status',
                        choices=[
                            ('agendada', 'Agendada'),
                            ('confirmada', 'Confirmada'),
                            ('cancelada', 'Cancelada'),
                            ('concluida', 'Concluída')
                        ],
                        default='agendada')
    
    # Campos de recorrência
    recorrente = BooleanField('Agendar recorrentemente')
    recorrencia_tipo = SelectField('Frequência',
                                  choices=[
                                      ('', 'Selecione...'),
                                      ('semanal', 'Semanal (toda semana)'),
                                      ('quinzenal', 'Quinzenal (a cada 2 semanas)'),
                                      ('mensal', 'Mensal (todo mês)')
                                  ],
                                  validators=[Optional()])
    recorrencia_periodo = SelectField('Por quanto tempo?',
                                     choices=[
                                         ('', 'Selecione...'),
                                         ('3meses', '3 meses'),
                                         ('6meses', '6 meses'),
                                         ('1ano', '1 ano')
                                     ],
                                     validators=[Optional()])
    
    submit = SubmitField('Salvar Agendamento')

class FiltroAgendaForm(FlaskForm):
    data_inicio = DateField('Data Início', format='%Y-%m-%d')
    data_fim = DateField('Data Fim', format='%Y-%m-%d')
    paciente_id = SelectField('Paciente', 
                             choices=[('', 'Todos os pacientes')])
    status = SelectField('Status',
                        choices=[
                            ('', 'Todos os status'),
                            ('agendada', 'Agendada'),
                            ('confirmada', 'Confirmada'),
                            ('cancelada', 'Cancelada'),
                            ('concluida', 'Concluída')
                        ])
    submit = SubmitField('Filtrar')
