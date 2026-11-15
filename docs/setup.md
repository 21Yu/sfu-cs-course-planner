# Local Setup

This guide covers the FastAPI backend, the PostgreSQL database and the React
frontend. Full Docker setup will be documented as issue #35 is completed.

## Prerequisites

- Git
- Python 3.12 (the version used by CI)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/), to run
  PostgreSQL locally

The frontend uses Vite, which requires Node.js 20.19+ or 22.12+, and npm.

## Get the code

1. Fork https://github.com/sfuosdev/sfu-cs-course-planner on GitHub.
2. Clone your fork and add the official repository as `upstream`:

   ```bash
   git clone https://github.com/YOUR_USERNAME/sfu-cs-course-planner.git
   cd sfu-cs-course-planner
   git remote add upstream https://github.com/sfuosdev/sfu-cs-course-planner.git
   git remote -v
   ```

## Set up and run the backend

Create a virtual environment in the `backend` directory, activate it and install
the backend dependencies:

```bash
cd backend
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run all backend commands (the server, tests, migrations and the seed script) from
`backend/` with this environment active, so Python can find the `app` package.

Copy `.env.example` to `.env` in the repository root to override the defaults.
The app reads `APP_NAME`, `APP_VERSION`, `APP_ENV`, `DEBUG`, `DATABASE_URL`,
`SFU_COURSES_API_BASE_URL`, and `SFU_COURSES_API_TIMEOUT_SECONDS` from that file
or from the process environment. The `/courses` endpoint accepts optional `dept`
and `number` query parameters and returns course outline data from sfucourses.
Upstream errors return 502 and upstream timeouts return 504.

Start the development server from the `backend` directory:

```bash
python -m uvicorn app.main:app --reload
```

The API is available at <http://127.0.0.1:8000>. The liveness endpoint is
`/health`, and `/health/db` checks the database connection. Interactive Swagger
documentation is at `/docs`, ReDoc is at `/redoc`, and the OpenAPI schema is at
`/openapi.json`.

## Set up the database

The backend stores its data in PostgreSQL 16, which runs locally in Docker. Make
sure Docker Desktop is running before you start.

### Start PostgreSQL

From the repository root:

```bash
docker compose up -d
```

This starts two containers: `db` (PostgreSQL on port 5432) and `adminer` (a
database browser on port 8080). Check that both are running with
`docker compose ps`. Data is kept in a Docker volume, so it survives
`docker compose stop` and restarts.

The default connection settings match `compose.yml`, so you don't need a `.env`
file:

```
DATABASE_URL="postgresql+psycopg://planner:planner@localhost:5432/course_planner"
```

### Create the tables

Tables are created by [Alembic](https://alembic.sqlalchemy.org/) migrations in
`backend/alembic/versions/`. From the `backend` directory:

```bash
alembic upgrade head
```

Run this again whenever you pull changes that add new migrations.

### Load sample data

From the `backend` directory:

```bash
python -m app.seed
```

This adds a few terms, a few CMPT courses and a prerequisite, so you have data to
develop against. It skips rows that already exist, so it is safe to run more than
once. The full course catalogue is loaded separately (#13).

### Browse the database

Open <http://localhost:8080> and log in to Adminer with:

| Field    | Value            |
| -------- | ---------------- |
| System   | `PostgreSQL`     |
| Server   | `db`             |
| Username | `planner`        |
| Password | `planner`        |
| Database | `course_planner` |

Click a table in the sidebar to see its rows, or use **SQL command** to run a
query. Adminer's row counts show `?` for PostgreSQL; open the table to see its
data.

### Change the schema

Models live in `backend/app/models/`. After changing a model, from the `backend`
directory:

1. Generate a migration:

   ```bash
   alembic revision --autogenerate -m "describe your change"
   ```

2. Read the new file in `backend/alembic/versions/` and check it does what you
   expect. Autogenerate can miss or misread some changes.
3. Apply it:

   ```bash
   alembic upgrade head
   ```

4. Commit the migration file together with the model change.

New models must be imported in `backend/app/models/__init__.py`, or Alembic
won't see them.

### Reset the database

To delete all data and start again, from the repository root:

```bash
docker compose down -v
docker compose up -d
```

Then repeat [Create the tables](#create-the-tables) and
[Load sample data](#load-sample-data). The `-v` flag deletes the data volume, so
only use it when you want an empty database. Use `docker compose stop` to stop
the database and keep its data.

## Run backend tests

From the `backend` directory:

```bash
python -m pytest
```

The tests don't need a database.

## Run the frontend

From the repository root:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite (usually `http://localhost:5173`). To create
and preview a production build, run `npm run build` and then `npm run preview`
from `frontend/`.
