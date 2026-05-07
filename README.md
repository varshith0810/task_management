# 🗂 TaskFlow — Team Task Manager

Full-stack team project & task management app.  
**Backend**: FastAPI + SQLAlchemy | **Frontend**: React + Vite | **Deploy**: Railway

---

## 📁 Project Structure

```
team-task-manager/
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── main.py           # App factory (also serves frontend in prod)
│   │   ├── api/v1/
│   │   │   ├── router.py
│   │   │   ├── deps.py
│   │   │   └── endpoints/
│   │   │       ├── auth.py
│   │   │       ├── projects.py
│   │   │       ├── tasks.py
│   │   │       └── dashboard.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── db/session.py
│   │   ├── models/models.py
│   │   └── schemas/schemas.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/                 # React + Vite app
│   ├── src/
│   │   ├── api/client.js     # API client (all endpoints)
│   │   ├── context/AuthContext.jsx
│   │   ├── components/       # Layout, UI components
│   │   └── pages/            # Login, Signup, Dashboard, Projects
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── Dockerfile                # Multi-stage: builds frontend → embeds in backend
├── railway.toml              # Railway deploy config
└── README.md
```

---

## 🚀 Local Development

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env         # Edit SECRET_KEY and DATABASE_URL
uvicorn app.main:app --reload
# API → http://localhost:8000
# Docs → http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
# Create .env.local:
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev
# App → http://localhost:5173
```

---

## 🚂 Deploy to Railway

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
gh repo create taskflow --public --push
# or push to your existing GitHub repo
```

### Step 2 — Create Railway project

1. Go to [railway.app](https://railway.app) → **New Project**
2. Choose **Deploy from GitHub repo**
3. Select your repository

### Step 3 — Add PostgreSQL

1. In your Railway project → **New Service → Database → PostgreSQL**
2. Railway will automatically set `DATABASE_URL` in your environment

### Step 4 — Set environment variables

In Railway → your service → **Variables**, add:

| Variable | Value |
|---|---|
| `SECRET_KEY` | `openssl rand -hex 32` (generate a secure key) |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` |
| `ALLOWED_ORIGINS` | `https://your-app.railway.app` |
| `DEBUG` | `false` |

> `DATABASE_URL` is set automatically by the PostgreSQL add-on.

### Step 5 — Deploy

Railway will automatically:
1. Detect the `Dockerfile`
2. Build the React frontend (Stage 1)
3. Bundle it into the Python backend (Stage 2)
4. Start the server

Your app will be live at `https://your-app.railway.app` 🎉

---

## 🏗 How the Production Build Works

The `Dockerfile` is multi-stage:

```
Stage 1 (node:20-alpine)
  └── npm install && npm run build → /app/frontend/dist

Stage 2 (python:3.12-slim)
  └── pip install requirements
  └── copy backend source
  └── copy /dist → /static
  └── FastAPI serves /static/index.html for all non-API routes
```

This means **one Railway service** serves both the API (`/api/v1/...`) and the React SPA.

---

## 🔐 Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./task_manager.db` | DB connection (use PostgreSQL in prod) |
| `SECRET_KEY` | *(required)* | JWT signing secret |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token TTL |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS origins, comma-separated |
| `DEBUG` | `false` | Enable SQL echo |

---

## 📡 API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/auth/signup` | Register |
| POST | `/api/v1/auth/login` | Login → tokens |
| POST | `/api/v1/auth/refresh` | Refresh tokens |
| GET | `/api/v1/auth/me` | Current user |
| GET | `/api/v1/projects` | List my projects |
| POST | `/api/v1/projects` | Create project |
| GET | `/api/v1/projects/{id}` | Project detail |
| PATCH | `/api/v1/projects/{id}` | Update project |
| DELETE | `/api/v1/projects/{id}` | Archive project |
| POST | `/api/v1/projects/{id}/members` | Add member |
| GET | `/api/v1/projects/{id}/tasks` | List tasks |
| POST | `/api/v1/projects/{id}/tasks` | Create task |
| PATCH | `/api/v1/projects/{id}/tasks/{tid}` | Update task |
| DELETE | `/api/v1/projects/{id}/tasks/{tid}` | Delete task |
| GET | `/api/v1/dashboard` | Dashboard stats |

Interactive docs: `https://your-app.railway.app/docs`
