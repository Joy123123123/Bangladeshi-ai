# 🚀 Setup Guide — Bangladeshi-ai

This guide walks you through running **Bangladeshi-ai** locally, whether you prefer Docker or a manual Python setup.

---

## Prerequisites

| Tool | Minimum Version | Install |
|------|----------------|---------|
| Python | 3.10+ | [python.org](https://python.org) |
| pip | 23+ | bundled with Python |
| Git | any | [git-scm.com](https://git-scm.com) |
| Docker *(optional)* | 24+ | [docker.com](https://docker.com) |
| PostgreSQL *(optional, local)* | 14+ | [postgresql.org](https://postgresql.org) |
| Redis *(optional, local)* | 7+ | [redis.io](https://redis.io) |

---

## Option A: Docker (Recommended)

The fastest way to get a fully working stack (API + PostgreSQL + Redis) running.

```bash
# 1. Clone the repository
git clone https://github.com/Joy123123123/Bangladeshi-ai.git
cd Bangladeshi-ai/backend

# 2. Configure environment
cp .env.example .env
# Open .env in your editor and add your AI API keys

# 3. Start all services
docker compose up --build
```

The API will be available at **http://localhost:8000**
Interactive docs at **http://localhost:8000/docs**

---

## Option B: Manual Python Setup

### 1. Clone and navigate

```bash
git clone https://github.com/Joy123123123/Bangladeshi-ai.git
cd Bangladeshi-ai/backend
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` in your editor and fill in the values:

```env
GEMINI_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
GROK_API_KEY=your_key_here
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/bangladeshi_ai
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=generate_a_random_secret_here
```

> **Getting free API keys:**
> - **Gemini** → https://aistudio.google.com/app/apikey
> - **DeepSeek** → https://platform.deepseek.com/api_keys
> - **Grok** → https://console.x.ai/

### 5. Start the development server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at **http://localhost:8000**

---

## API Quick Test

Once the server is running, test it:

```bash
# Health check
curl http://localhost:8000/health

# Chat with Gemini
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "আমাকে পাইথন শেখাও", "model": "gemini"}'

# Study helper
curl -X POST http://localhost:8000/api/v1/study/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What is photosynthesis?", "subject": "science"}'

# Grammar check
curl -X POST http://localhost:8000/api/v1/grammar/check \
  -H "Content-Type: application/json" \
  -d '{"text": "আমি ভাল আছি। তুমি কেমন?"}'

# Code help
curl -X POST http://localhost:8000/api/v1/code/help \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I reverse a list in Python?", "programming_language": "python"}'
```

Visit **http://localhost:8000/docs** for the full interactive Swagger UI.

---

## Deployment (Free Tier)

### Railway
1. Create an account at [railway.app](https://railway.app)
2. Connect your GitHub repo
3. Add environment variables in the Railway dashboard
4. Deploy — Railway auto-detects FastAPI

### Render
1. Create an account at [render.com](https://render.com)
2. Create a new **Web Service** and connect your GitHub repo
3. Set **Build Command**: `pip install -r backend/requirements.txt`
4. Set **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables and deploy

### Heroku
```bash
heroku login
heroku create bangladeshi-ai
heroku config:set GEMINI_API_KEY=xxx DEEPSEEK_API_KEY=xxx ...
git push heroku main
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Activate venv and run `pip install -r requirements.txt` |
| `Connection refused` (DB) | Start PostgreSQL or use Docker Compose |
| `401 Unauthorized` (AI) | Check your API keys in `.env` |
| Port 8000 in use | Use `--port 8001` or kill the other process |

---

For more help, open an issue at [github.com/Joy123123123/Bangladeshi-ai/issues](https://github.com/Joy123123123/Bangladeshi-ai/issues).
