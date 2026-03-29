# 🎓 বাংলাদেশী AI শিক্ষা প্ল্যাটফর্ম

> **THE** free AI education platform built specifically for Bangladeshi students — NCTB curriculum, SSC/HSC, BUET, DU, Medical & BCS preparation in Bengali.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)
![React](https://img.shields.io/badge/React-18-blue?logo=react)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## 🌟 Features

| Feature | Description |
|---------|-------------|
| 🤖 **Multi-Model AI** | Gemini, DeepSeek, Grok — automatic routing & fallback |
| 📚 **NCTB Context** | Class 9–12 curriculum injection, board-specific (Dhaka, Rajshahi, etc.) |
| 🔤 **Banglish Parser** | Romanised Bengali detected & normalised automatically |
| 🎯 **Admission RAG** | Previous-year questions for BUET, DU, Medical, BCS from ChromaDB |
| 📶 **Data Saver Mode** | Image compression, streaming chunks — optimised for 2G/3G |
| ⚡ **Streaming** | Real-time SSE streaming so students see answers instantly |
| 🌍 **Bengali-First** | All system prompts written in Bengali for quality responses |
| 🆓 **100% Free** | All AI APIs have free tiers — no paywalls |

---

## 🏗️ Project Structure

```
Bangladeshi-ai/
├── app/                          # FastAPI backend
│   ├── core/
│   │   ├── config.py             # Settings (API keys, NCTB config)
│   │   └── prompts_bn.py         # Bengali system prompts
│   ├── api/v1/endpoints/
│   │   └── chat.py               # Streaming + non-streaming chat endpoints
│   ├── services/
│   │   ├── banglish_parser.py    # Banglish → Bengali normalisation
│   │   ├── nctb_context_service.py # NCTB curriculum context injection
│   │   ├── rag_service.py        # ChromaDB RAG (previous-year questions)
│   │   └── ai_routing_service.py # Multi-model routing (Gemini/DeepSeek/Grok)
│   ├── models/
│   │   └── schemas.py            # Pydantic v2 request/response models
│   ├── middleware/
│   │   └── nctb_middleware.py    # NCTB context header extraction
│   ├── utils/
│   │   └── data_saver.py         # Image compression, response chunking
│   └── main.py                   # FastAPI app entry point
│
├── src/                          # React frontend
│   ├── components/
│   │   └── ChatUI.jsx            # Streaming chat UI with Data Saver toggle
│   ├── hooks/
│   │   └── useDataSaver.js       # Low-data mode hook
│   ├── utils/
│   │   └── banglishConverter.js  # Client-side Banglish detection & hints
│   ├── pages/
│   │   └── StudyDashboard.jsx    # Subject/Class selector + quick-launch
│   ├── main.jsx                  # React entry point
│   └── index.css                 # Tailwind + Bengali typography
│
├── .env.example                  # Environment variables template
├── requirements.txt              # Python dependencies
├── package.json                  # Node.js dependencies
├── docker-compose.yml            # Full-stack Docker setup
├── Dockerfile                    # Backend Docker image
├── Dockerfile.frontend           # Frontend Docker image (nginx)
├── tailwind.config.js            # Mobile-first Tailwind config
└── vite.config.js                # Vite bundler config
```

---

## 🚀 Quick Start

### 1. Clone & configure

```bash
git clone https://github.com/Joy123123123/Bangladeshi-ai.git
cd Bangladeshi-ai

# Copy environment template
cp .env.example .env
# Fill in at least one API key (GEMINI_API_KEY recommended)
```

### 2. Backend (FastAPI)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000
```

API docs available at: **http://localhost:8000/docs**

### 3. Frontend (React)

```bash
# Install dependencies
npm install

# Start development server
npm run dev
# → http://localhost:3000
```

### 4. Docker (Full Stack)

```bash
# Copy and fill .env
cp .env.example .env

# Start everything
docker compose up --build

# Frontend: http://localhost
# API:      http://localhost:8000
# API docs: http://localhost:8000/docs
```

---

## 🔑 Getting Free API Keys

| Provider | Free Tier | Link |
|----------|-----------|------|
| **Google Gemini** | 15 RPM, 1M tokens/day | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| **DeepSeek** | Generous free credits | [platform.deepseek.com](https://platform.deepseek.com/) |
| **Grok (xAI)** | Free tier available | [console.x.ai](https://console.x.ai/) |

---

## 📡 API Reference

### POST `/api/v1/chat/stream`
Streaming SSE chat with NCTB context injection.

```json
{
  "message": "নিউটনের গতিসূত্র ব্যাখ্যা করো",
  "class_level": 10,
  "subject": "physics",
  "exam_type": "SSC",
  "board": "Dhaka",
  "data_saver_mode": false,
  "preferred_model": "auto",
  "include_rag": true
}
```

**Response**: `text/event-stream` — each event: `data: {"content": "...", "done": false}`

### POST `/api/v1/chat`
Non-streaming (collect full response).

### GET `/api/v1/subjects`
List all NCTB subjects with Bengali names.

### GET `/api/v1/classes`
List supported class levels and education boards.

### GET `/api/v1/health`
Health check + list of available AI models.

---

## 🇧🇩 Bangladesh-Specific Features

### NCTB Context Layer
When a student selects *Class 10 + Physics + Dhaka Board*, the system automatically injects:
```
আপনি দশম শ্রেণীর NCTB পদার্থবিজ্ঞানের বিশেষজ্ঞ শিক্ষক।
SSC পরীক্ষার জন্য গুরুত্বপূর্ণ বিষয়গুলোতে মনোযোগ দিন।
শিক্ষার্থী ঢাকা শিক্ষা বোর্ডের অধীনে পড়াশোনা করছে।
```

### Banglish Parser
Automatically handles input like:
- `"physics er newton law ki?"` → recognised as Physics question
- `"math solve koro"` → normalised to Bengali before LLM call

### Admission RAG
ChromaDB stores previous-year questions. When a student asks about BUET preparation, relevant questions and shortcuts are retrieved and injected as context.

### Data Saver Mode
- **Frontend**: Images compressed to ≤800px width at 60% quality (browser Canvas API)
- **Backend**: Response chunks emitted at half the normal size
- **Visual indicator**: Green badge shows KB saved

---

## 🤝 Contributing

All contributions are welcome! This is a community project for Bangladeshi students.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "Add my feature"`
4. Push & open a Pull Request

### Priority areas
- 📚 Adding NCTB question banks to ChromaDB
- 🌐 Improving Banglish ↔ Bengali conversion
- 🎨 UI improvements for low-end mobile devices
- 📖 Translating documentation to Bengali

---

## 📄 License

MIT License — free for everyone, forever.

---

## 🙏 Acknowledgements

Built for the students of Bangladesh 🇧🇩 — may this platform help every student achieve their dreams, regardless of their economic background.

*"শিক্ষাই জাতির মেরুদণ্ড"* — Education is the backbone of a nation.
