# YouTube Clone Hackathon Starter

A monorepo project with a FastAPI backend and a React TypeScript frontend.

## Features

- Front page listing all uploaded videos
- Video upload
- Video playback
- Comments on videos
- Recommended videos on watch page

## Project Structure

- `backend/`: FastAPI + SQLite API (managed with `uv`)
- `frontend/`: React + TypeScript web app (managed with `bun`)

## Run The Full Stack

```bash
make up
```

This builds and starts backend and frontend containers.

## Access

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## Stop

```bash
make down
```
