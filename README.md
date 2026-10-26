FastAPI com Docker, Docker Compose e Poetry

Projeto de API desenvolvido com FastAPI e preparado para execução em containers Docker, utilizando Docker Compose para configuração do ambiente e Poetry para gerenciamento de dependências.

Tecnologias
Python 3.14
FastAPI
Uvicorn
Poetry
Docker
Docker Compose
Pré-requisitos
Git
Docker instalado
Docker Compose disponível
Como executar
1. Clone o repositório
git clone URL_DO_REPOSITORIO

Entre na pasta do projeto:

cd fast-api-ex5-docker
2. Configure as variáveis de ambiente

Crie um arquivo chamado .env na raiz do projeto com o seguinte conteúdo:

PYTHONUNBUFFERED=1
3. Construa e inicie a aplicação
docker compose up --build -d
4. Acesse a aplicação

Documentação interativa da API:

http://localhost:8000/docs

Endpoint principal:

http://localhost:8000

5. Consulte os logs
docker compose logs -f api
6. Pare a aplicação
docker compose down
Dependências

As dependências são declaradas no arquivo pyproject.toml e instaladas pelo Poetry durante a construção da imagem.

O arquivo poetry.lock registra as versões resolvidas das dependências.

Estrutura do projeto
app.py: código-fonte da aplicação FastAPI.
Dockerfile: configuração da imagem da aplicação.
docker-compose.yml: configuração do serviço, das portas, dos volumes e das variáveis de ambiente.
pyproject.toml: configuração do projeto e dependências.
poetry.lock: versões resolvidas das dependências.
.dockerignore: arquivos excluídos do contexto de construção da imagem.
.gitignore: arquivos e pastas ignorados pelo Git.