# CloudPark - Docker Setup

Este projeto está configurado para rodar com Docker e Docker Compose.

## Pré-requisitos

- Docker
- Docker Compose

## Estrutura do Projeto

```
cloudpark/
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   └── ...
├── frontend/
│   ├── Dockerfile
│   ├── .dockerignore
│   └── ...
└── docker-compose.yml
```

## Como rodar as aplicações

### 1. Criar arquivo `.env` na raiz do projeto usando como base o `.env.example`

```bash
SECRET_KEY="django-insecure-omunt755isl)+0@+6+dqsnl4otcua^whl#$ro1qs6@nezq%9!2"
DEBUG=True
```

### 2. Construir e iniciar as aplicações

```bash
docker compose up --build
```

## Acessos

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/docs/

### Usuários criados via migration (como seed)

- Atendente
    - email: atendente@cloudpark.com
    - senha: atendente123
    - Acessar http://localhost:8000/
- Técnico
    - email: tecnico@cloudpark.com
    - senha: tecnico123
    - Acessar http://localhost:5173

## Como executar os testes automatizados

### Rodar comando no terminal para entrar no container de backend

```bash
docker compose exec backend sh
```

### Rodar comando para executar testes dentro do container

```bash
python3 manage.py test
```
