# 🌟 Bangladeshi-ai — বাংলাদেশী AI

<div align="center">

**A world-class, FREE AI platform for Bengali students and communities**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-teal.svg)](https://fastapi.tiangolo.com)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](docs/CONTRIBUTING.md)

[📖 Docs](docs/) · [🚀 Setup Guide](docs/SETUP_GUIDE.md) · [🤝 Contribute](docs/CONTRIBUTING.md) · [🗺️ Roadmap](docs/ROADMAP.md)

</div>

---

## 🎯 Vision

**Bangladeshi-ai** is a community-driven, open-source AI platform that combines the power of **DeepSeek, Gemini, Grok**, and other leading AI models to give every Bengali student access to world-class, free AI assistance — no paywalls, no limits.

Think **ChatGPT-level intelligence**, but built for and by the Bengali community. 🇧🇩

---

## 🌍 Core Mission

- 🎓 **Empower Bengali students** with free, high-quality AI education tools
- 🏛️ **Preserve Bengali culture** while leveraging cutting-edge AI
- 🤝 **Build a collaborative community** of developers, educators, and students
- 💬 **ChatGPT-like experience** optimised for Bengali language and culture
- 🆓 **100% Open Source & Free** — no paywalls, no limitations, ever

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **Multi-Model AI Chat** | Switch between Gemini, DeepSeek, Grok in one interface |
| 📚 **Study Helper** | Subject tutoring: Math, Science, History, Literature |
| ✏️ **Bengali Grammar Assistant** | Real-time grammar & essay improvement |
| 💻 **Code Assistant** | Programming help, debugging, algorithm explanations |
| 🗣️ **Voice Support** | Bengali speech-to-text & text-to-speech *(coming soon)* |
| 👥 **Community System** | Open contributions, feedback voting, discussion forums |

---

## 🏗️ Technology Stack

### Backend
- **Python 3.10+** with **FastAPI** for a lightning-fast API
- **LangChain** for multi-model AI orchestration
- **PostgreSQL** for user data and conversation history
- **Redis** for caching and session management
- **Docker** for easy, reproducible deployment

### AI Models
| Model | Provider | Free Tier |
|-------|----------|-----------|
| Gemini 1.5 Flash | Google | ✅ |
| DeepSeek Chat | DeepSeek | ✅ |
| Grok | X / Twitter | ✅ |
| Open-source (Llama, Mistral) | Hugging Face | ✅ |

### Frontend
- **React / Next.js** — modern, responsive UI
- **Bengali typography support**
- **Mobile-first design**

---

## 📂 Project Structure

```
Bangladeshi-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── models/              # Database models
│   │   ├── routes/              # API route handlers
│   │   ├── services/            # AI model integrations
│   │   ├── utils/               # Helpers, prompts, validators
│   │   └── middleware/          # Auth & rate limiting
│   ├── requirements.txt
│   ├── .env.example
│   └── docker-compose.yml
├── docs/
│   ├── API_DOCUMENTATION.md
│   ├── SETUP_GUIDE.md
│   ├── CONTRIBUTING.md
│   └── ROADMAP.md
├── README.md
├── CONTRIBUTORS.md
└── LICENSE
```

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Joy123123123/Bangladeshi-ai.git
cd Bangladeshi-ai

# 2. Set up the Python backend
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env and add your API keys

# 4. Run the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) to explore the API.

Full instructions → **[docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)**

---

## 🔑 Environment Variables

```env
# AI API Keys (get free keys from each provider)
GEMINI_API_KEY=your_gemini_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
GROK_API_KEY=your_grok_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/bangladeshi_ai

# Redis
REDIS_URL=redis://localhost:6379

# Security
JWT_SECRET=your_very_long_random_secret_here
```

---

## 👥 Community & Contributors

### Roles

| Role | Responsibilities |
|------|-----------------|
| 👑 **Founder / Commander** | Vision, architecture decisions, mentoring |
| 🛠️ **Core Contributors** | Feature development, code reviews |
| 📝 **Documentation** | Guides, tutorials, API docs |
| 🎨 **UI/UX Designers** | Frontend & user experience |
| 🌐 **NLP Specialists** | Bengali language optimisation |
| 🐛 **Community Testers** | Bug reports & feedback |

### How to Contribute

1. ⭐ Star the repository
2. 🍴 Fork the repository
3. 🌿 Create a feature branch (`git checkout -b feature/amazing-feature`)
4. 💾 Commit your changes (`git commit -m 'Add amazing feature'`)
5. 📤 Push to your branch (`git push origin feature/amazing-feature`)
6. 🔄 Open a Pull Request

Full guide → **[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)**

All contributors are recognised in **[CONTRIBUTORS.md](CONTRIBUTORS.md)** 🏆

---

## 📊 Roadmap

| Phase | Timeline | Status |
|-------|----------|--------|
| Phase 1: MVP | Weeks 1–4 | 🔄 In Progress |
| Phase 2: Multi-Model | Weeks 5–8 | 📋 Planned |
| Phase 3: Advanced Features | Weeks 9–12 | 📋 Planned |
| Phase 4: Community & Scale | Week 13+ | 📋 Planned |

Full roadmap → **[docs/ROADMAP.md](docs/ROADMAP.md)**

---

## 💰 Our Free & Open Source Commitment

- 🚫 **No paywalls** — All features free, forever
- 🚫 **No ads** — Clean, distraction-free experience
- ✅ **MIT License** — Do whatever you want with the code
- ✅ **Community-driven** — Decisions made with community input
- ✅ **Sustainable** — Grant-based funding and sponsorships

---

## 🎓 Bengali Culture Integration

This platform is built **for** Bangladeshis, **by** Bangladeshis:
- System prompts aware of Bangladeshi context, history, and values
- Study materials include Bangladeshi history, literature, and culture
- Examples relevant to Bengali students' everyday life
- Full Bengali language support with proper typography

---

## 📝 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Made with ❤️ for Bangladesh 🇧🇩**

[⭐ Star this repo](https://github.com/Joy123123123/Bangladeshi-ai) · [🐛 Report a Bug](https://github.com/Joy123123123/Bangladeshi-ai/issues) · [💡 Request a Feature](https://github.com/Joy123123123/Bangladeshi-ai/issues)

</div>
