# Docker Production Setup

Simple production-ready Docker Compose setup for WorkshopsAPI using environment variables.

## Quick Start

1. **Create environment file**:
   ```bash
   cp env.template .env
   # Edit .env with your production values
   ```

2. **Start all services**:
   ```bash
   sudo docker compose up -d
   ```

3. **View logs**:
   ```bash
   sudo docker compose logs -f
   ```

4. **Stop services**:
   ```bash
   sudo docker compose down
   ```

## Environment Configuration

### Required Variables

Create a `.env` file based on `env.template`:

```bash
# Database Configuration
POSTGRES_DB=workshops_db
POSTGRES_USER=workshops_user
POSTGRES_PASSWORD=your-secure-password
POSTGRES_PORT=5432

# Application Configuration
SECRET_KEY=your-secret-key-change-in-production
TOKEN_EXPIRE_TIME=60
API_JWT_TOKEN=your-jwt-token-here
IS_PROD=Prod

# Logging
LOG_LEVEL=INFO

# Port Configuration
BACKEND_PORT=9000
```

### Database URI

The `DATABASE_URI` is automatically constructed from the PostgreSQL variables:
```
DATABASE_URI=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
```

## Services

- **PostgreSQL**: Database on port `${POSTGRES_PORT:-5432}`
- **Backend**: FastAPI application on port `${BACKEND_PORT:-9000}`

## Security Best Practices

1. **Change default passwords**:
   - Update `POSTGRES_PASSWORD` with a strong password
   - Update `SECRET_KEY` with a secure random string
   - Update `API_JWT_TOKEN` with your actual JWT token

2. **Use different ports for production**:
   ```bash
   POSTGRES_PORT=5433
   BACKEND_PORT=9001
   ```

3. **Set production logging**:
   ```bash
   LOG_LEVEL=WARNING
   IS_PROD=Prod
   ```

## Database Migrations

```bash
# Run migrations
sudo docker compose exec backend uv run alembic upgrade head

# Create new migration
sudo docker compose exec backend uv run alembic revision --autogenerate -m "description"
```

## Access Points

- **API**: http://localhost:${BACKEND_PORT:-9000}
- **Documentation**: http://localhost:${BACKEND_PORT:-9000}/docs
- **Health Check**: http://localhost:${BACKEND_PORT:-9000}/health

## Management Commands

```bash
# Restart backend
sudo docker compose restart backend

# View backend logs
sudo docker compose logs -f backend

# Access database
sudo docker compose exec postgres psql -U ${POSTGRES_USER:-workshops_user} -d ${POSTGRES_DB:-workshops_db}

# Backup database
sudo docker compose exec postgres pg_dump -U ${POSTGRES_USER:-workshops_user} ${POSTGRES_DB:-workshops_db} > backup.sql
```

## Environment-Specific Configurations

### Development
```bash
# .env.dev
IS_PROD=Dev
LOG_LEVEL=DEBUG
BACKEND_PORT=9001
POSTGRES_PORT=5433
```

### Production
```bash
# .env.prod
IS_PROD=Prod
LOG_LEVEL=WARNING
SECRET_KEY=your-production-secret-key
API_JWT_TOKEN=your-production-jwt-token
```

## Production Notes

- Uses pre-built Python image (no build required)
- Volume mounts for live code updates
- Health checks for database
- Automatic restart on failure
- Persistent database storage
- Environment-based configuration
- Secure by default with environment variables 