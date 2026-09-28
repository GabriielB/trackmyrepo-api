FROM python:3.14-slim
## copiando o uv pra gerenciar o ambiente virutal
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

## copiando as dependências
COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-install-project

COPY app ./app

EXPOSE 8000

CMD ["uv", "run", "--no-sync", "fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]