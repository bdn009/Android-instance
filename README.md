# ☁️ CloudRoid — Cloud Android Instance Manager

A full-stack web platform for running and controlling Android applications inside server-hosted Waydroid environments. Users can start, stop, stream, and interact with Android instances directly from their browser.

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat&logo=tailwindcss&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)

---

## Architecture

```
User Browser
    ↓
React Dashboard (Tailwind CSS)
    ↓
Nginx Reverse Proxy
    ↓
FastAPI Backend (JWT Auth)
    ↓
┌──────────────────┬─────────────┐
│ Instance Manager │   Redis     │
│  (Waydroid CLI)  │  (Queue)    │
└──────────────────┴─────────────┘
    ↓
Waydroid Android Containers
```

## Features

- **JWT Authentication** — Register, login, token-based access
- **Instance Management** — Create, start, stop, delete Android containers
- **Live Screen Streaming** — View Android screen via WebSocket in the browser
- **Touch Input** — Tap and swipe on the streaming canvas
- **APK Management** — Upload and install APK files into instances
- **Real-time Updates** — WebSocket-based live status sync on the dashboard
- **Resource Monitoring** — CPU/RAM tracking, instance queuing
- **Rate Limiting** — Token bucket per IP
- **Dockerized Deployment** — One command to spin up all services

---

## Prerequisites

| Component | Version |
|-----------|---------|
| Docker & Docker Compose | v20+ / v2+ |
| Node.js (for local dev) | 20+ |
| Python (for local dev)  | 3.12+ |
| Ubuntu (for Waydroid)   | 24.04 LTS |

---

## Quick Start (Docker)

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd "Android instance"
```

### 2. Configure environment

```bash
cp backend/.env.example backend/.env
# Edit backend/.env and set a strong SECRET_KEY
```

### 3. Launch all services

```bash
docker compose up -d
```

This starts:
- **Frontend** → `http://localhost:3000`
- **Backend API** → `http://localhost:8000`
- **API Docs** → `http://localhost:8000/docs`
- **PostgreSQL** → `localhost:5432`
- **Redis** → `localhost:6379`

### 4. (Production) Setup Waydroid on the host

```bash
sudo bash infrastructure/scripts/setup.sh
```

---

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start with auto-reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server runs on `http://localhost:3000` and proxies API calls to `:8000`.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login, returns JWT |
| `GET`  | `/auth/me` | Get current user |
| `GET`  | `/instances` | List user's instances |
| `POST` | `/instances/create` | Create new instance |
| `POST` | `/instances/{id}/start` | Start instance |
| `POST` | `/instances/{id}/stop` | Stop instance |
| `DELETE` | `/instances/{id}` | Delete instance |
| `POST` | `/apk/upload` | Upload APK file |
| `GET`  | `/apk` | List uploaded APKs |
| `POST` | `/apk/{id}/install/{instance_id}` | Install APK |
| `WS`   | `/ws/stream/{id}` | Live screen stream |
| `WS`   | `/ws/updates` | Dashboard status feed |
| `GET`  | `/health` | Health check |

---

## Project Structure

```
root/
├── backend/
│   ├── app/
│   │   ├── api/          # Route handlers
│   │   │   ├── auth.py
│   │   │   ├── instances.py
│   │   │   ├── apk.py
│   │   │   └── streaming.py
│   │   ├── services/     # Business logic
│   │   │   ├── instance_manager.py
│   │   │   └── resource_monitor.py
│   │   ├── models/       # ORM & schemas
│   │   │   ├── models.py
│   │   │   └── schemas.py
│   │   ├── database/
│   │   │   └── database.py
│   │   ├── config.py
│   │   ├── middleware.py
│   │   └── logging_config.py
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # Reusable UI
│   │   │   ├── Navbar.jsx
│   │   │   ├── InstanceCard.jsx
│   │   │   ├── LiveStream.jsx
│   │   │   └── ApkUpload.jsx
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── RegisterPage.jsx
│   │   │   └── DashboardPage.jsx
│   │   ├── services/     # State & API
│   │   │   ├── api.js
│   │   │   ├── authStore.js
│   │   │   └── instanceStore.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── infrastructure/
│   └── scripts/
│       ├── setup.sh
│       └── health_check.sh
├── docker-compose.yml
└── README.md
```

---

## Health Check

```bash
bash infrastructure/scripts/health_check.sh
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `SECRET_KEY` | (change me) | JWT signing key |
| `APK_UPLOAD_DIR` | `./uploads/apks` | APK storage path |
| `MAX_INSTANCES_PER_USER` | `5` | Instance limit per user |

---

## License

MIT
