## Quick Start Commands

### 1. Environment Setup
```
# Copy environment file and edit with your values
cp .env.example .env
nano .env
```

### 2. Database Migration
```
# Initialize Alembic
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 3. Start Services
```
# Terminal 1: Start Redis and PostgreSQL (if not running as services)
redis-server
sudo systemctl start postgresql

# Terminal 2: Start Celery worker
celery -A app.tasks.gemini_tasks worker --loglevel=info

# Terminal 3: Start FastAPI application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Test API
```
# Test health endpoint
curl http://localhost:8000/health

# Test signup
curl -X POST "http://localhost:8000/auth/signup" \
     -H "Content-Type: application/json" \
     -d '{"mobile_number": "+1234567890", "name": "Test User"}'
```

## Docker Deployment (Alternative)

### docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://gemini_user:password@db:5432/gemini_backend
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./app:/app

  worker:
    build: .
    command: celery -A app.tasks.gemini_tasks worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://gemini_user:password@db:5432/gemini_backend
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./app:/app

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: gemini_backend
      POSTGRES_USER: gemini_user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
