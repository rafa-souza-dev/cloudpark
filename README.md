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

## Como Executar

### 1. Construir e iniciar todos os serviços

```bash
docker-compose up --build
```

### 2. Executar em background

```bash
docker-compose up -d --build
```

### 3. Parar os serviços

```bash
docker-compose down
```

### 4. Parar e remover volumes

```bash
docker-compose down -v
```

## Acessos

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin

## Volumes

O projeto utiliza volumes para persistir dados:

- `backend_data`: Armazena o banco SQLite do Django
- `./backend:/app`: Volume para desenvolvimento (mapeia o código local)

## Comandos Úteis

### Executar migrações do Django

```bash
docker-compose exec backend python manage.py migrate
```

### Criar superusuário

```bash
docker-compose exec backend python manage.py createsuperuser
```

### Acessar shell do backend

```bash
docker-compose exec backend python manage.py shell
```

### Ver logs

```bash
# Todos os serviços
docker-compose logs

# Apenas backend
docker-compose logs backend

# Apenas frontend
docker-compose logs frontend
```

## Desenvolvimento

Para desenvolvimento, você pode usar o volume mapeado no backend:

```bash
# O código local será refletido no container
docker-compose up backend
```

## Variáveis de Ambiente

As variáveis de ambiente estão definidas no `docker-compose.yml`:

- `DEBUG=True`: Modo debug do Django
- `SECRET_KEY`: Chave secreta do Django (altere em produção)

## Notas

- O backend usa SQLite como banco de dados
- O frontend é servido pelo Nginx
- Os dados do banco são persistidos no volume `backend_data`
- Para produção, considere usar um banco de dados mais robusto como PostgreSQL 