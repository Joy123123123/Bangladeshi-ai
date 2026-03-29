# 🗺️ Roadmap — Bangladeshi-ai

This document outlines the planned development phases for **Bangladeshi-ai**.

> **Last updated:** March 2026

---

## Phase 1: MVP (Weeks 1–4) 🔄 In Progress

### Backend
- [x] Python backend setup with FastAPI
- [x] Project structure (routes, services, models, middleware)
- [x] Gemini API integration
- [x] DeepSeek API integration
- [x] Grok API integration
- [x] Bengali NLP utilities (language detection, text preprocessing)
- [x] Authentication system (JWT)
- [x] Rate limiting middleware
- [x] Environment configuration
- [x] Docker setup

### API Endpoints
- [x] `POST /api/v1/chat/` — Multi-model AI chat
- [x] `POST /api/v1/study/` — Study helper
- [x] `POST /api/v1/grammar/check` — Grammar & writing assistant
- [x] `POST /api/v1/code/help` — Code assistant
- [x] `POST /api/v1/users/register` — User registration
- [x] `POST /api/v1/users/login` — User login

### Documentation
- [x] README.md
- [x] SETUP_GUIDE.md
- [x] CONTRIBUTING.md
- [x] API_DOCUMENTATION.md
- [x] CONTRIBUTORS.md

### Deployment
- [ ] Deploy backend to Railway/Render (free tier)
- [ ] Set up CI/CD with GitHub Actions
- [ ] Domain name setup

---

## Phase 2: Multi-Model Enhancement (Weeks 5–8) 📋 Planned

### AI Features
- [ ] Conversation history (store in PostgreSQL)
- [ ] Multi-turn chat (pass history to AI models)
- [ ] Model performance benchmarking
- [ ] Context window management
- [ ] Streaming responses (Server-Sent Events)

### Bengali Language
- [ ] Improved Bengali text normalisation
- [ ] Bengali spell checker integration
- [ ] Transliteration (Bangla ↔ English phonetic)
- [ ] Bengali OCR (image to text)

### Infrastructure
- [ ] PostgreSQL integration (replace in-memory store)
- [ ] Redis caching for repeated queries
- [ ] Celery for background tasks
- [ ] Proper logging (structlog)
- [ ] Health check dashboard

---

## Phase 3: Advanced Features (Weeks 9–12) 📋 Planned

### Study Helper
- [ ] Subject-specific knowledge bases
- [ ] Practice problems with AI feedback
- [ ] Exam preparation mode
- [ ] Progress tracking per student
- [ ] Personalised study recommendations

### Voice Support
- [ ] Bengali speech-to-text (Whisper API)
- [ ] Text-to-speech in Bengali
- [ ] Voice chat interface

### Code Assistant
- [ ] Code execution sandbox
- [ ] Project idea generator
- [ ] Algorithm visualizer descriptions
- [ ] Code review with explanations

### Mobile
- [ ] React Native mobile app (iOS & Android)
- [ ] Offline mode for basic features
- [ ] Push notifications

---

## Phase 4: Community & Scale (Weeks 13+) 📋 Planned

### Community
- [ ] GitHub Discussions integration
- [ ] Community voting on feature requests
- [ ] Public contribution leaderboard
- [ ] Contributor badge system
- [ ] Monthly community calls

### Open Source Models
- [ ] Llama 3 integration (via Hugging Face)
- [ ] Mistral integration
- [ ] Fine-tuned Bengali language model
- [ ] Self-hosted model option

### Multi-language
- [ ] Full Bengali UI translation
- [ ] Support for other South Asian languages (Hindi, Urdu)
- [ ] Bilingual (Bengali + English) response mode

### Production Scale
- [ ] Load balancing
- [ ] Auto-scaling on cloud
- [ ] CDN for static assets
- [ ] Monitoring & alerting (Prometheus + Grafana)
- [ ] GDPR / data privacy compliance

---

## 💡 Future Ideas (Backlog)

| Idea | Priority | Status |
|------|----------|--------|
| Bengali essay grading AI | High | 📋 Planned |
| Virtual tutor avatar | Medium | 💭 Idea |
| Peer tutoring marketplace | Medium | 💭 Idea |
| AI-powered study groups | Low | 💭 Idea |
| Integration with Bangladeshi school curricula | High | 📋 Planned |
| Scholarship finder AI | Medium | 💭 Idea |
| Career guidance chatbot | Medium | 💭 Idea |

---

## 📊 Key Success Metrics

| Metric | Target (6 months) |
|--------|-----------------|
| Active users | 10,000+ |
| GitHub Stars | 1,000+ |
| Contributors | 100+ |
| API uptime | 99.9% |
| Avg response time | < 3 seconds |

---

*Want to help us reach these goals? Read our [Contributing Guide](CONTRIBUTING.md)!*
