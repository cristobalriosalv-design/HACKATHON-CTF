# EIATube Hackathon Starter

This repo is the code that is going to be given to the students as part of the hackathon challenge

The challenge in the hackathon is for students to take an app and make it support an stress test of thousands of concurrent users.

They will receive the current code in the repo that is a local working EIATube copy, but that has been vibecoded and is full of possible optimization.

The idea is that they optimize the code and create an infrastructure in Azure (if we get the sponsorship, we are in talks), and at the end of the hackathon run a stress test in this infrastructure they deployed. The team that supports the most ammount of concurrent users without breaking wins.

## Run the project

This project is designed to run with `docker compose` on any PC or VM (including a plain EC2 machine) without external managed services.

### Option 1: Docker Compose (recommended)

Requirements:
- Docker Engine + Docker Compose plugin
- Open ports `5173` and `8000`

From the repository root:

```bash
docker compose up --build -d
```

Then open:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API health check: http://localhost:8000/health
- Interactive API docs: http://localhost:8000/docs
- OpenAPI schema: http://localhost:8000/openapi.json

Common commands:

```bash
# watch logs
docker compose logs -f

# restart services
docker compose restart

# stop and remove containers
docker compose down
```

### One-machine deployment example (EC2 or any Linux VM)

Use this flow when you create a VM and want one command-driven deployment:

```bash
# 1) install docker + git (example for Ubuntu)
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER
newgrp docker

# 2) clone and run
git clone <your-repo-url> EIATube
cd EIATube
docker compose up --build -d
```

To update after new commits:

```bash
git pull
docker compose up --build -d
```

### Architecture in this compose setup

- `backend` runs FastAPI with Uvicorn workers (no dev reload).
- `frontend` runs a built Vite app in preview mode.
- Uploads persist in Docker volume `eiatube_uploads`.
- No external DB is required; SQLite runs inside backend container storage.

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

## API endpoints

The complete live contract is always available in `/docs` and `/openapi.json`.

### System

- `GET /health` - health status.

### Videos

- `GET /videos?limit=<int>&offset=<int>` - list videos.
- `POST /videos/upload` - upload video (`multipart/form-data` with `title`, `description`, `file`, optional `thumbnail`, optional `uploader_id`).
- `GET /videos/{video_id}` - get one video (read-only).
- `POST /videos/{video_id}/views` - increment views for a video.
- `DELETE /videos/{video_id}?requester_user_id=<int>` - delete a video (owner only).
- `GET /videos/{video_id}/stream` - stream video file or redirect to external media origin.
- `GET /videos/{video_id}/thumbnail` - return thumbnail file or redirect.
- `GET /videos/{video_id}/comments?limit=<int>&offset=<int>` - list comments.
- `POST /videos/{video_id}/comments` - create comment (`application/json`: `author`, `content`).
- `GET /videos/{video_id}/recommended` - list recommended videos.

### Users and subscriptions

- `GET /users?limit=<int>&offset=<int>` - list users.
- `POST /users` - create user (`multipart/form-data` with `display_name`, optional `provider`, `provider_subject`, `email`, `avatar`).
- `GET /users/providers` - list available providers.
- `GET /users/{user_id}/avatar` - return avatar file or redirect.
- `POST /users/{user_id}/subscriptions/{creator_id}` - subscribe to creator.
- `DELETE /users/{user_id}/subscriptions/{creator_id}` - unsubscribe.
- `GET /users/{user_id}/subscriptions?limit=<int>&offset=<int>` - list subscribed creator IDs.
- `GET /users/{user_id}/feed?limit=<int>&offset=<int>` - subscription feed videos.

## Media offload deployment examples

The backend supports redirecting media requests (`/videos/{id}/stream`, `/videos/{id}/thumbnail`, `/users/{id}/avatar`) to external media hosting when `MEDIA_BASE_URL` is set.

If `MEDIA_BASE_URL` is not set, media is served locally from `uploads/` (dev fallback).

### 1) Nginx reverse proxy to `/uploads`

Use Nginx to serve files from your backend uploads origin:

```nginx
location /uploads/ {
    proxy_pass http://media-origin.internal/uploads/;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

Set backend environment:

```bash
MEDIA_BASE_URL=https://media.example.com/uploads
```

### 2) S3-compatible object storage URL pattern

If uploads are replicated to an S3-compatible bucket and exposed by URL path:

```bash
MEDIA_BASE_URL=https://storage.example.com/eiatube-uploads
```

Then API media endpoints redirect to paths like:

```text
https://storage.example.com/eiatube-uploads/thumbnails/<file>.jpg
https://storage.example.com/eiatube-uploads/avatars/<file>.png
https://storage.example.com/eiatube-uploads/<video>.mp4
```

### 3) Cloudflare CDN in front of media origin

Put Cloudflare in front of your media origin (Nginx/S3/R2), then point backend redirects at the CDN domain:

```bash
MEDIA_BASE_URL=https://cdn.example.com/uploads
```

Recommended:
- Cache static media aggressively at Cloudflare (long TTL for versioned filenames).
- Enable origin shield/proxy caching to reduce origin load.
- Purge by URL if you need immediate media invalidation.
