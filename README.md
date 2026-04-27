# EIATube Hackathon Starter

This repo is the code that is going to be given to the students as part of the hackathon challenge

The challenge in the hackathon is for students to take an app and make it support an stress test of thousands of concurrent users.

They will receive the current code in the repo that is a local working EIATube copy, but that has been vibecoded and is full of possible optimization.

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
