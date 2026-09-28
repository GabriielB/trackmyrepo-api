# TrackMyRepo API

Backend do **TrackMyRepo**, responsável pelas regras de negócio, persistência dos dados e integração com a GitHub REST API.

A API foi desenvolvida com FastAPI e PostgreSQL e é consumida pelo frontend disponível no repositório `trackmyrepo-web` `https://github.com/GabriielB/trackmyrepo-web`.

> Para instruções de execução da aplicação completa com Docker Compose, consulte também o README do repositório `trackmyrepo-web` `https://github.com/GabriielB/trackmyrepo-web`.

---

## Tecnologias

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- HTTPX
- Psycopg
- PostgreSQL
- uv
- Docker

---

## Responsabilidades

A API é responsável por:

- receber requisições do frontend;
- validar dados de entrada;
- consultar a GitHub REST API;
- transformar os dados recebidos do GitHub;
- persistir informações no PostgreSQL;
- listar projetos monitorados;
- atualizar informações dos projetos;
- remover projetos;
- filtrar projetos favoritos.

---

## Arquitetura interna

A aplicação utiliza uma separação simples de responsabilidades:

```
API
 ↓
Services
 ↙       ↘
Models   Integrations
 ↓           ↓
PostgreSQL  GitHub REST API
```

Estrutura principal:

```
app/
├── api/
├── core/
├── integrations/
├── models/
├── schemas/
├── services/
└── main.py
```

### Organização

- `api`: definição dos endpoints HTTP;
- `services`: regras e fluxos da aplicação;
- `integrations`: comunicação com serviços externos;
- `models`: modelos persistidos no banco;
- `schemas`: contratos de entrada e saída;
- `core`: infraestrutura compartilhada, como conexão com banco.

---

## Fluxo de uma requisição

Exemplo ao cadastrar um repositório:

```
Frontend
   ↓
POST /projects
   ↓
FastAPI
   ↓
Project Service
   ↓
GitHub REST API
   ↓
PostgreSQL
   ↓
Resposta ao frontend
```

---

## Endpoints

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/health` | Verifica se a API está disponível |
| GET | `/projects` | Lista os projetos monitorados |
| GET | `/projects/{project_id}` | Busca um projeto específico |
| POST | `/projects` | Adiciona um repositório |
| PUT | `/projects/{project_id}` | Atualiza informações do projeto |
| DELETE | `/projects/{project_id}` | Remove um projeto |
| POST | `/projects/{project_id}/refresh` | Atualiza os dados consultando novamente o GitHub |

Também é possível listar somente os favoritos:

```
GET /projects?favorite=true
```

---

## Swagger

Com a API em execução, a documentação interativa pode ser acessada em:

```
http://localhost:8000/docs
```

---

## Health Check

A API disponibiliza:

```
GET /health
```

Exemplo de resposta:

```
{
  "status": "ok",
  "mensagem": "TrackMyRepo API funcionando."
}
```

Esse endpoint é utilizado como uma verificação simples de disponibilidade da API.

---

# GitHub REST API

A API externa utilizada pelo projeto é a **GitHub REST API**.

O endpoint principal consumido é:

```
GET /repos/{owner}/{repo}
```

Exemplo:

```
GET /repos/flutter/flutter
```

Documentação oficial:

```
https://docs.github.com/en/rest/repos/repos#get-a-repository
```

O backend consulta o GitHub e transforma a resposta antes de persistir os dados.

Entre os campos utilizados estão:

- ID do repositório;
- owner;
- nome;
- nome completo;
- descrição;
- linguagem;
- stars;
- forks;
- issues abertas;
- branch principal;
- status de arquivamento;
- URL;
- data da última atualização;
- data do último push.

---

## Autenticação na GitHub API

O MVP trabalha apenas com repositórios públicos.

Por isso, a variável:

```
GITHUB_TOKEN
```

é opcional.

Sem um token, ainda é possível consultar repositórios públicos.

Um token pode ser utilizado para aumentar os limites de requisições da GitHub REST API.

---

# Persistência

O projeto utiliza PostgreSQL.

As principais tabelas são:

```
tracked_projects
github_repositories
```

---

## `tracked_projects`

Armazena dados pertencentes ao TrackMyRepo, como:

```
display_name
notes
favorite
created_at
updated_at
```

---

## `github_repositories`

Armazena os dados sincronizados da GitHub REST API, como:

```
github_id
owner
name
full_name
description
language
stars
forks
open_issues_count
default_branch
archived
visibility
html_url
github_updated_at
github_pushed_at
last_synced_at
```

Na versão atual do MVP, a relação entre projeto monitorado e repositório é 1:1.

---

# Executando a aplicação completa

A forma recomendada de executar o projeto é através do Docker Compose disponível no repositório:

```
[trackmyrepo-web] https://github.com/GabriielB/trackmyrepo-web
```

# Executando somente a API localmente

## Pré-requisitos

Para executar fora do Docker:

- Python;
- uv;
- PostgreSQL em execução.

---

## 1. Instale as dependências

Na raiz do backend:

```bash
uv sync
```

---

## 2. Configure o banco

Por padrão, a aplicação utiliza: POSTGRESQL


Também é possível definir:

```
DATABASE_URL
```

---

## 3. Inicie a API

```bash
uv run fastapi dev app/main.py
```

A API ficará disponível em:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

# Variáveis de ambiente

## `DATABASE_URL`

Define a conexão com o PostgreSQL.

Exemplo:

---

## `GITHUB_TOKEN`

Opcional.

Pode ser utilizado para autenticar as chamadas feitas à GitHub REST API.

Exemplo:

```text
GITHUB_TOKEN=github_pat_xxxxxxxxx
```

Não é necessário para testar o MVP com repositórios públicos.

---

# Docker

Este repositório possui seu próprio:

```text
Dockerfile
```

O container expõe a porta:

```text
8000
```

A execução integrada com frontend e PostgreSQL é feita pelo `compose.yml` existente no repositório `trackmyrepo-web`.

---

# Criação das tabelas

Nesta versão do MVP, as tabelas são criadas automaticamente na inicialização utilizando:

```python
Base.metadata.create_all(...)
```

O projeto ainda não utiliza migrations com Alembic.


---

# Teste rápido da API

Com o projeto completo em execução, acesse:

```text
http://localhost:8000/docs
```

No Swagger, é possível testar os endpoints diretamente.

Exemplo de cadastro:

```json
{
  "repository": "flutter/flutter"
}
```

Endpoint:

```http
POST /projects
```

Depois é possível testar:

```http
GET /projects
```

```http
PUT /projects/{project_id}
```

```http
POST /projects/{project_id}/refresh
```

```http
DELETE /projects/{project_id}
```
