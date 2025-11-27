🏋️‍♂️ SonicFit - Backend API

Backend Flask para o sistema de acompanhamento fitness SonicFit, com autenticação JWT, gestão de rotinas alimentares, metas de peso e cálculo de calorias.
📋 Índice

    Funcionalidades

    Tecnologias

    Estrutura do Projeto

    Instalação e Configuração

    Variáveis de Ambiente

    Rotas da API

    Modelos de Dados

    Autenticação

    Execução

🚀 Funcionalidades
🔐 Autenticação & Usuário

    Registro e login com telefone/senha

    Tokens JWT com refresh automático

    Gestão de perfil do usuário

    Middleware de autenticação

🍽️ Rotina Alimentar

    Rotinas padrão por período (Café, Almoço, Lanche, Janta, Ceia)

    Seleção de proteínas com cálculo automático de calorias

    Marcação de refeições como concluídas

    Cálculo de calorias totais do dia

    Persistência das escolhas do usuário

🎯 Metas de Peso

    Definição de peso atual e meta

    Histórico de evolução de peso

    Acompanhamento de progresso

💪 Atividades Físicas

    Registro de atividades do dia

    Histórico de atividades

    Integração com rotina alimentar

🔢 Cálculos Automáticos

    Cálculo de TMB (Taxa Metabólica Basal)

    Balanço calórico diário

    Calorias por refeição baseadas nas escolhas

🛠 Tecnologias

    Python 3.8+

    Flask - Framework web

    Flask-SQLAlchemy - ORM para banco de dados

    Flask-JWT-Extended - Autenticação JWT

    Flask-CORS - Cross-Origin Resource Sharing

    Flask-Migrate - Migrações de banco de dados

    Python-dotenv - Variáveis de ambiente

    Bcrypt - Hash de senhas

📁 Estrutura do Projeto
text

#sonicfit-backend/
#├── app/
#│   ├── __init__.py              # Inicialização do app Flask
#│   ├── models.py               # Modelos de banco de dados
#│   ├── routes/
#│   │   ├── __init__.py
#│   │   ├── auth.py            # Rotas de autenticação
#│   │   ├── user.py            # Rotas de usuário
#│   │   ├── rotina.py          # Rotas de rotina alimentar
#│   │   ├── metas.py           # Rotas de metas
#│   │   └── atividades.py      # Rotas de atividades
#│   ├── utils.py               # Funções utilitárias
#│   └── config.py              # Configurações
#├── migrations/                 # Migrações do banco
#├── instance/
#│   └── config.py              # Configurações de instância
#├── requirements.txt           # Dependências
#├── run.py                    # Arquivo de execução
#└── .env.example              # Exemplo de variáveis de ambiente

⚙️ Instalação e Configuração
1. Clone o repositório
bash

git clone <seu-repositorio>
cd sonicfit-backend

2. Crie um ambiente virtual
bash

python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

3. Instale as dependências
bash

pip install -r requirements.txt

4. Configure as variáveis de ambiente
bash

cp .env.example .env
# Edite o .env com suas configurações

🔧 Variáveis de Ambiente
env

FLASK_ENV=development
FLASK_APP=run.py
SECRET_KEY=sua_chave_super_secreta_aqui
JWT_SECRET_KEY=sua_chave_jwt_super_secreta

# Banco de dados
DATABASE_URL=sqlite:///sonicfit.db
# ou para PostgreSQL:
# DATABASE_URL=postgresql://usuario:senha@localhost/sonicfit

# Configurações JWT
JWT_ACCESS_TOKEN_EXPIRES=3600  # 1 hora
JWT_REFRESH_TOKEN_EXPIRES=604800  # 7 dias

- 🚀 Rotas da API

-🔐 Autenticação
Método	Rota	Descrição
POST	/api/auth/cadastro	Registro de novo usuário
POST	/api/auth/login	Login do usuário
POST	/api/auth/refresh	Refresh token

-👤 Usuário
Método	Rota	Descrição
GET	/api/user/me	Dados do usuário logado
PUT	/api/user/update	Atualizar perfil

-🍽️ Rotina Alimentar
Método	Rota	Descrição
GET	/api/rotina/hoje	Rotina do dia atual
POST	/api/rotina/marcar	Marcar/atualizar refeição
GET	/api/rotina/calorias-totais	Calorias consumidas no dia

-🎯 Metas
Método	Rota	Descrição
GET	/api/metas	Listar metas do usuário
GET	/api/metas/ultima	Última meta definida
POST	/api/metas/criar	Criar nova meta
GET	/api/metas/historico	Histórico de peso

-💪 Atividades
Método	Rota	Descrição
GET	/api/atividades/hoje	Atividades do dia
POST	/api/atividades/registrar	Registrar atividade
GET	/api/atividades/historico	Histórico de atividades
🗄 Modelos de Dados
User
python

id, telefone, nome, email, data_nascimento, genero, altura, senha_hash, created_at, updated_at

RotinaAlimentar
python

id, user_id, periodo, refeicao, data, proteina_selecionada, concluido, calorias, created_at, updated_at

Meta
python

id, user_id, peso_atual, peso_meta, data_inicio, ativa, created_at

HistoricoPeso
python

id, user_id, peso, data_registro, created_at

-🔐 Autenticação

Todas as rotas (exceto login/cadastro) requerem autenticação JWT:
http

Authorization: Bearer <seu_token_jwt>

Fluxo de Autenticação:

    Login/Cadastro → Retorna access_token e refresh_token

    Requests Autenticados → Incluir access_token no header

    Token Expirado → Usar refresh_token para obter novo access_token

-🏃 Execução
Desenvolvimento:
bash

python run.py

Ou usando Flask:
bash

flask run

Migrações do Banco:
bash

flask db init           # Primeira vez
flask db migrate        # Criar migração
flask db upgrade        # Aplicar migração

📊 Exemplos de Uso
Marcar Refeição:
javascript

// POST /api/rotina/marcar
{
  "periodo": "Almoço",
  "proteina_selecionada": "Frango grelhado 150g",
  "concluido": true
}

Criar Meta:
javascript

// POST /api/metas/criar
{
  "peso_atual": 85.5,
  "peso_meta": 75.0
}

🐛 Troubleshooting
Erros Comuns:

    __init__() got an unexpected keyword argument 'data'

        Verifique os parâmetros do construtor do modelo RotinaAlimentar

    Erro de CORS

        Verifique se o Flask-CORS está configurado corretamente

    Token expirado

        Implemente refresh token automaticamente na API

    Erro de banco de dados

        Execute as migrações: flask db upgrade

👨‍💻 Desenvolvido por

Alfredo Allan
💪 Foco, disciplina e código!

Versão: 1.0.0
Última atualização: Dezembro 2024
