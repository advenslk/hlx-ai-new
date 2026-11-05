# HELZERX AI Support - PostgreSQL Database Setup Guide

HELZERX uses **PostgreSQL 16+** with **SQLAlchemy 2.0 (asyncpg)** and **Alembic** migrations.

---

## 1. Quick Start with Docker (Recommended)

Run PostgreSQL with a persistent volume:

```bash
docker run -d \
  --name helzerx-postgres \
  -e POSTGRES_USER=helzerx_user \
  -e POSTGRES_PASSWORD=helzerx_secure_pass \
  -e POSTGRES_DB=helzerx_support \
  -p 5432:5432 \
  -v helzerx_pg_data:/var/lib/postgresql/data \
  postgres:16-alpine
```

---

## 2. Native PostgreSQL Installation (Ubuntu/Debian)

```bash
sudo apt update && sudo apt install -y postgresql postgresql-contrib

# Switch to postgres user
sudo -u postgres psql
```

Inside the PostgreSQL prompt (`psql`):

```sql
CREATE DATABASE helzerx_support;
CREATE USER helzerx_user WITH ENCRYPTED PASSWORD 'helzerx_secure_pass';
GRANT ALL PRIVILEGES ON DATABASE helzerx_support TO helzerx_user;
\c helzerx_support
GRANT ALL ON SCHEMA public TO helzerx_user;
\q
```

---

## 3. Environment String Configuration

Set the database URLs in your `.env` file:

```env
# Async connection for the running bot:
DATABASE_URL="postgresql+asyncpg://helzerx_user:helzerx_secure_pass@localhost:5432/helzerx_support"

# Synchronous connection for Alembic migrations:
SYNC_DATABASE_URL="postgresql+psycopg2://helzerx_user:helzerx_secure_pass@localhost:5432/helzerx_support"
```

---

## 4. Running Migrations

Apply Alembic migrations to create all tables and indexes:

```bash
alembic upgrade head
```

Verify database tables:
```bash
python3 scripts/setup_db.py
```

---

## 5. Local Development Fallback

If `SQLITE_FALLBACK=true` is enabled in `.env` and PostgreSQL is not reachable, HELZERX will safely fall back to `sqlite+aiosqlite:///helzerx_support.db` to prevent downtime during offline development.
