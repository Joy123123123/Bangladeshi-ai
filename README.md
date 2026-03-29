# 🌏 Bangladeshi-AI – Asia's Free AI Education Platform

A **production-ready FastAPI backend** that provides Bengali-language AI tutoring for Bangladeshi students. Built on NCTB curriculum with SSE streaming, multi-model AI routing, RAG-powered context, and mobile-first design.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Redis (optional – degrades gracefully without it)
- MongoDB (optional – chat history disabled without it)
- At least one AI API key (Gemini / DeepSeek / Grok)

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/Joy123123123/Bangladeshi-ai.git
cd Bangladeshi-ai

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your API keys

# 5. Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Visit **http://localhost:8000/docs** for the interactive API documentation.

---

## 🐳 Docker Compose (Full Stack)

```bash
cp .env.example .env
# Edit .env with your API keys
docker-compose up -d
```

Services:
- **API**: http://localhost:8000
- **MongoDB**: localhost:27017
- **Redis**: localhost:6379

---

## 📁 Project Structure

```
app/
├── core/
│   ├── config.py          # Pydantic v2 settings
│   ├── prompts_bn.py      # Bengali system prompts
│   └── constants.py       # NCTB curriculum constants
├── models/
│   └── schemas.py         # Pydantic v2 request/response models
├── services/
│   ├── ai_router.py       # Multi-model AI routing (Gemini/DeepSeek/Grok)
│   ├── rag_service.py     # ChromaDB vector search
│   ├── banglish_parser.py # Romanised Bengali normalisation
│   ├── nctb_context_service.py  # Curriculum context injection
│   ├── admission_engine.py      # Exam pattern recognition
│   └── cache_service.py   # Redis caching
├── repositories/
│   ├── conversation_repo.py  # Chat history (MongoDB)
│   └── user_repo.py          # User profiles (MongoDB)
├── api/v1/endpoints/
│   ├── chat.py            # SSE streaming chat
│   ├── study.py           # Study helpers (summaries, flashcards, quizzes)
│   └── admission.py       # Admission prep (BUET, DU, Medical, BCS)
├── middleware/
│   ├── nctb_middleware.py # NCTB context header extraction
│   ├── data_saver.py      # Low-data mode detection
│   ├── rate_limit.py      # Per-IP rate limiting (Redis)
│   └── auth.py            # JWT authentication helpers
├── utils/
│   ├── image_processor.py # Pillow image compression
│   ├── stream_generator.py # SSE chunk generator
│   └── validators.py      # Input validation
└── main.py                # FastAPI app factory
frontend/
└── src/components/ChatUI.jsx  # React mobile-first chat UI
```

---

## 🔑 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/chat/stream` | SSE streaming chat |
| `POST` | `/api/v1/chat` | Non-streaming chat |
| `POST` | `/api/v1/study/stream` | Study helper (summaries, flashcards, quizzes) |
| `POST` | `/api/v1/admission/stream` | Admission prep (BUET, DU, Medical, BCS) |
| `GET`  | `/api/v1/admission/strategy/{exam_type}` | Exam strategy & marks breakdown |
| `GET`  | `/api/v1/subjects` | List NCTB subjects |
| `GET`  | `/api/v1/classes` | List class levels & boards |
| `GET`  | `/api/v1/health` | Health check |

---

## 🤖 Supported AI Models

| Model | Provider | Best For |
|-------|----------|---------|
| `gemini` | Google | General education, Bengali language |
| `deepseek` | DeepSeek | Math, STEM, reasoning |
| `grok` | xAI | General knowledge |
| `auto` | — | Auto-selects best model |

---

## 📱 Features

- ✅ **SSE Streaming** – Real-time response streaming
- ✅ **Banglish Support** – Auto-normalises romanised Bengali
- ✅ **NCTB Context** – Classes 9–12, all boards, all subjects
- ✅ **RAG** – Previous-year exam questions via ChromaDB
- ✅ **Data Saver Mode** – 3G/4G optimised responses
- ✅ **Multi-Model** – Gemini + DeepSeek + Grok with fallback
- ✅ **Rate Limiting** – Per-IP via Redis
- ✅ **JWT Auth** – Optional authentication
- ✅ **Mobile-First** – React UI with Tailwind CSS

---

## 🎓 Target Exams

- SSC (মাধ্যমিক স্কুল সার্টিফিকেট)
- HSC (উচ্চ মাধ্যমিক সার্টিফিকেট)
- BUET (বুয়েট ভর্তি)
- Dhaka University (ঢাবি ভর্তি)
- Medical Admission (মেডিকেল ভর্তি)
- BCS (বিসিএস প্রিলি ও লিখিত)
