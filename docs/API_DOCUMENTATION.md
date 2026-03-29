# 📖 API Documentation — Bangladeshi-ai

Base URL: `http://localhost:8000` (development)

Interactive docs (Swagger): `http://localhost:8000/docs`
ReDoc: `http://localhost:8000/redoc`

All endpoints return JSON. Errors follow the format:
```json
{"detail": "Error description here"}
```

---

## Health

### `GET /`
Returns a welcome message and API version.

**Response**
```json
{
  "message": "বাংলাদেশী AI — Welcome! The platform is running. 🇧🇩",
  "version": "0.1.0",
  "docs": "/docs"
}
```

### `GET /health`
Simple health check.

**Response**
```json
{"status": "ok"}
```

---

## Chat — `/api/v1/chat`

### `GET /api/v1/chat/models`
List all available AI models.

**Response**
```json
{
  "models": ["deepseek", "gemini", "grok"],
  "default": "gemini"
}
```

---

### `POST /api/v1/chat/`
Send a message to an AI model and receive a response.

**Request Body**
```json
{
  "message": "আমাকে পাইথন শেখাও",
  "model": "gemini",
  "conversation_id": null,
  "language": "auto"
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `message` | string | ✅ | — | User message (1–8000 chars) |
| `model` | string | ❌ | `"gemini"` | `gemini`, `deepseek`, or `grok` |
| `conversation_id` | string | ❌ | auto-generated | UUID for conversation continuity |
| `language` | string | ❌ | `"auto"` | `auto`, `bn` (Bengali), or `en` (English) |

**Response**
```json
{
  "model": "gemini",
  "content": "পাইথন একটি অত্যন্ত জনপ্রিয় প্রোগ্রামিং ভাষা...",
  "conversation_id": "3f7a1b2c-...",
  "tokens_used": null,
  "history": null
}
```

**Rate Limit:** 20 requests/minute per IP

---

## Study Helper — `/api/v1/study`

### `POST /api/v1/study/`
Ask a subject-specific study question.

**Request Body**
```json
{
  "question": "What is the quadratic formula?",
  "subject": "math",
  "model": "gemini"
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `question` | string | ✅ | — | Study question |
| `subject` | string | ❌ | `"general"` | `math`, `science`, `history`, `literature`, `general` |
| `model` | string | ❌ | `"gemini"` | AI model to use |

**Response**
```json
{
  "model": "gemini",
  "content": "The quadratic formula is: x = (-b ± √(b²-4ac)) / 2a ...",
  "conversation_id": null,
  "tokens_used": null,
  "history": null
}
```

---

## Grammar & Writing — `/api/v1/grammar`

### `POST /api/v1/grammar/check`
Check and improve grammar in Bengali or English text.

**Request Body**
```json
{
  "text": "আমি গতকাল বাজার গিয়েছিলাম এবং অনেক কিছু কিনেছি।",
  "language": "auto",
  "model": "gemini"
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `text` | string | ✅ | — | Text to check (1–8000 chars) |
| `language` | string | ❌ | `"auto"` | `auto`, `bn`, or `en` |
| `model` | string | ❌ | `"gemini"` | AI model to use |

**Response**
```json
{
  "model": "gemini",
  "content": "Your text looks good! Here are some minor improvements...",
  "conversation_id": null,
  "tokens_used": null,
  "history": null
}
```

---

## Code Assistant — `/api/v1/code`

### `POST /api/v1/code/help`
Get AI-powered programming help.

**Request Body**
```json
{
  "question": "Why is my loop not working?",
  "code": "for i in range(10)\n    print(i)",
  "programming_language": "python",
  "model": "gemini"
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `question` | string | ✅ | — | Your programming question |
| `code` | string | ❌ | null | Code snippet (up to 16,000 chars) |
| `programming_language` | string | ❌ | `"python"` | Language name |
| `model` | string | ❌ | `"gemini"` | AI model to use |

**Response**
```json
{
  "model": "gemini",
  "content": "I can see a syntax error on line 1. You're missing the colon...",
  "conversation_id": null,
  "tokens_used": null,
  "history": null
}
```

---

## Users — `/api/v1/users`

### `POST /api/v1/users/register`
Register a new user account.

**Request Body**
```json
{
  "username": "rahman_student",
  "email": "rahman@example.com",
  "password": "secure_password_123",
  "full_name": "Rahman Ahmed"
}
```

**Response** `201 Created`
```json
{"message": "Account created successfully! Welcome to Bangladeshi-ai 🇧🇩"}
```

---

### `POST /api/v1/users/login`
Log in to receive JWT tokens.

**Request Body**
```json
{
  "username": "rahman_student",
  "password": "secure_password_123"
}
```

**Response**
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

Use the `access_token` in the `Authorization: Bearer <token>` header for protected endpoints.

---

## Error Codes

| Status | Meaning |
|--------|---------|
| `200` | Success |
| `201` | Created |
| `400` | Bad Request — check your request body |
| `401` | Unauthorised — missing or invalid token |
| `404` | Not Found |
| `409` | Conflict — e.g. username already taken |
| `422` | Validation Error — field failed validation |
| `429` | Too Many Requests — rate limit exceeded |
| `503` | Service Unavailable — AI API error |
