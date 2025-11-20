---
title: TDS Quiz Solver
emoji: 🧠
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# TDS Quiz Solver - Automated Quiz-Solving System

Complete automated quiz-solving system for the TDS LLM Analysis challenge. This system receives quiz challenges via webhook, scrapes JavaScript-rendered web pages, processes files (PDF, CSV, Excel), analyzes data, and submits answers automatically.

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

## 📊 Features

- ✅ FastAPI webhook endpoint for quiz challenges
- ✅ Playwright headless browser (Docker) or requests fallback (Python)
- ✅ PDF, CSV, Excel file processing
- ✅ Automated data analysis and answer generation
- ✅ Quiz chain solving (multiple sequential quizzes)
- ✅ Background task processing
- ✅ Rate limiting to prevent abuse
- ✅ Comprehensive error handling and logging
- ✅ Chart generation for visualization questions

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

## 🛠️ Development

Full documentation, installation instructions, and development guide available in the [GitHub repository](https://github.com/udayprattap/quiz-solver).

## 📄 License

MIT License - See LICENSE file for details.

---

**Built with**: FastAPI • Playwright • pandas • pdfplumber • matplotlib
