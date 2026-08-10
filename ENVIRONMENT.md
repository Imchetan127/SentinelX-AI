# SentinelX AI — Local & Containerized Environment Configuration Guide

## 1. Environment Setup Path Used
- **Primary Deployment Target**: Docker Compose (`docker-compose.yml`) containing PostgreSQL (`postgres:15-alpine`), FastAPI Backend, Next.js Frontend, and Adminer.
- **Local Host Development Fallback (Active Setup)**: 
  - **Docker Status**: Docker engine binary (`docker`) is NOT installed/available on this host machine.
  - **Active Setup**: Native Host execution utilizing local PostgreSQL 16 server (`sentinelx_db` database) on `localhost:5432` with `.env.local` configuration overrides.

---

## 2. Quick Start Steps (Clean Clone Setup)

### Option A: Local Host Development (No Docker)
1. **Prerequisites**: Ensure PostgreSQL 16 and Python 3.12+ / Node.js 18+ are installed.
2. **Start Local PostgreSQL**:
   ```bash
   brew services start postgresql@16
   psql -d postgres -c "CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD 'postgres';" 2>/dev/null || true
   createdb -O postgres sentinelx_db 2>/dev/null || true
   ```
3. **Environment Overrides**: `.env.local` is present in the repository root containing:
   ```env
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=sentinelx_db
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sentinelx_db
   ```
4. **Backend Setup & Migrations**:
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   PYTHONPATH=. alembic upgrade head
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
5. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

### Option B: Docker Compose (Production & Containerized Dev)
1. **Ensure Docker Engine & Docker Compose are running**:
   ```bash
   docker compose up -d --build
   ```
2. **Verify Services**:
   - Backend: `http://localhost:8000/health`
   - Frontend: `http://localhost:3000`
   - Adminer Database UI: `http://localhost:8080`

---

## 3. Database Architecture & SQLite Cleanup Summary
- **Primary Database Engine**: PostgreSQL (SQLAlchemy + Asyncpg/Psycopg2).
- **SQLite Resolution**:
  - `backend/sentinelx.db` was an un-tracked stray database file created during manual host execution.
  - It has been removed from disk (`rm backend/sentinelx.db`).
  - `DATABASE_URL` is the single source of truth for runtime database resolution.
  - The Pytest suite (`backend/tests/`) continues to use fast, isolated in-memory SQLite (`sqlite:///:memory:`) for test idempotency (78/78 tests passing).
