---
title: TDS Quiz Solver
emoji: 🧠
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
---

# 🧠 TDS Quiz Solver

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![Playwright](https://img.shields.io/badge/Playwright-1.40.0-45ba4b.svg)](https://playwright.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Automated Quiz-Solving System for TDS LLM Analysis Challenge**

Intelligent webhook-based system that automatically receives quiz URLs, scrapes web pages, processes data files (PDF/CSV/Excel), analyzes questions, generates answers, and submits them—all within a 3-minute window.

## 🚀 Quick Start on Hugging Face Spaces

This Space provides a `/solve` endpoint that accepts quiz URLs and automatically solves them.

### Required Environment Variables

Configure these in your Space Settings → Variables & Secrets:

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `EMAIL` | ✅ Yes | `your.email@example.com` | Your registered email |
| `SECRET` | ✅ Yes | `your_secret_key` | Your authentication secret |
| `DISABLE_PLAYWRIGHT` | Optional | `0` | Set to `1` for Python Space (requests-only mode) |
| `RATE_LIMIT_WINDOW` | Optional | `300` | Rate limit window in seconds |
| `RATE_LIMIT_MAX` | Optional | `40` | Max requests per IP per window |
| `ENABLE_SELF_PING` | Optional | `0` | Set to `1` to keep Space awake |

### API Endpoints

#### Health Check
```bash
curl https://USERNAME-quiz-solver.hf.space/
```

#### Solve Quiz
```bash
curl -X POST https://USERNAME-quiz-solver.hf.space/solve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your.email@example.com",
    "secret": "your_secret_key",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

#### System Info
```bash
curl https://USERNAME-quiz-solver.hf.space/info
```

## 🐳 Docker vs Python Space

### Docker Space (Recommended)
- ✅ Full Playwright browser support
- ✅ Complete JavaScript rendering
- ✅ Handles dynamic content
- ⚠️ Slightly longer startup time

### Python Space
- ✅ Faster startup
- ⚠️ Set `DISABLE_PLAYWRIGHT=1`
- ⚠️ Limited to static HTML (requests-only)
- ⚠️ May not handle complex JS-heavy pages

---

## 📊 Key Features

- **FastAPI Webhook**: `/solve` endpoint for quiz challenges
- **Browser Automation**: Playwright Chromium (Docker) or requests fallback (Python)
- **Multi-Format Processing**: PDF, CSV, Excel file support
- **Smart Analysis**: Automated data analysis and answer generation
- **Quiz Chains**: Handles multiple sequential quizzes
- **Background Tasks**: Non-blocking async processing
- **Rate Limiting**: IP-based abuse prevention
- **Error Handling**: 3-minute timeout with retry logic
- **Chart Generation**: Base64 PNG for visualization questions

## 🔧 Supported Question Types

- **Numeric**: Sum, total, count, average, mean, median, max, min
- **Boolean**: True/false, yes/no questions
- **Charts**: Bar charts, line plots, scatter plots, histograms (Base64 PNG)
- **Complex**: JSON objects with multiple values

## 📝 Response Format

### Success Response (202 Accepted)
```json
{
  "status": "processing",
  "message": "Quiz solving started for URL: https://example.com/quiz"
}
```

### Error Responses
- `403 Forbidden`: Invalid secret or email mismatch
- `422 Unprocessable Entity`: Invalid request format
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

## 📚 Full Documentation

Comprehensive installation, usage, and development guide available in the [GitHub repository](https://github.com/udayprattap/quiz-solver).

**Quick Links**:
- 📖 [Complete README](https://github.com/udayprattap/quiz-solver/blob/main/README.md)
- 📋 [Project Summary](https://github.com/udayprattap/quiz-solver/blob/main/PROJECT_SUMMARY.md)
- 🧪 [Testing Guide](https://github.com/udayprattap/quiz-solver#testing)
- 🚀 [Deployment Options](https://github.com/udayprattap/quiz-solver#deployment)

---

## 📄 License

MIT License - See [LICENSE](https://github.com/udayprattap/quiz-solver/blob/main/LICENSE) file for details.

---

## 🛠️ Built With

**Core**: FastAPI • Python 3.10 • Playwright • Docker

**Data**: pandas • pdfplumber • openpyxl • BeautifulSoup4

**Viz**: matplotlib • seaborn

**More**: [Full Tech Stack](https://github.com/udayprattap/quiz-solver#tech-stack)

---

## 📞 Contact

**GitHub**: [udayprattap/quiz-solver](https://github.com/udayprattap/quiz-solver)

**Email**: 24ds3000019@ds.study.iitm.ac.in

---

**Status**: ✅ Production Ready | 🚀 Live on Hugging Face Spaces
