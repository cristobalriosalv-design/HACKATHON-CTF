# YouTube Clone Hackathon Starter

This repo is the code that is going to be given to the students as part of the hackathon challenge

The challenge in the hackathon is for students to take an app and make it support an stress test of thousands of concurrent users.

They will receive the current code in the repo that is a local working Youtube copy, but that has been vibecoded and is full of possible optimization.

The idea is that they optimize the code and create an infrastructure in Azure (if we get the sponsorship, we are in talks), and at the end of the hackathon run a stress test in this infrastructure they deployed. The team that supports the most ammount of concurrent users without breaking wins.

## Run the project

You can run this project either with Docker (fastest setup) or locally.

### Option 1: Run with Docker Compose

Requirements:
- Docker
- Docker Compose

From the repository root:

```bash
docker compose up --build
```

Then open:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Health check: http://localhost:8000/health

Stop services with:

```bash
docker compose down
```

### Option 2: Run locally (without Docker)

Requirements:
- Python 3.12+
- `uv` (for Python dependency management)
- Bun (for frontend dependencies and dev server)

#### 1) Start backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2) Start frontend (new terminal)

```bash
cd frontend
bun install
bun run dev
```

Then open:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Health check: http://localhost:8000/health
