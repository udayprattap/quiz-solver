# 🧠 TDS Quiz Solver

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Playwright](https://img.shields.io/badge/Playwright-1.40.0-45ba4b.svg)](https://playwright.dev/)

**Automated Quiz-Solving System for TDS LLM Analysis Challenge**

An intelligent webhook-based system that automatically receives quiz URLs, scrapes web pages with Playwright, processes data files (PDF/CSV/Excel), analyzes questions using keyword detection and data science techniques, generates accurate answers, and submits them—all within a 3-minute timeout window.

---

## 📑 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Project Structure](#-project-structure)
- [License](#-license)
- [Contact](#-contact)

---

## ✨ Features

### Core Capabilities
- **Webhook Endpoint**: FastAPI-powered `/solve` endpoint for receiving quiz challenges
- **Intelligent Browser Automation**: Playwright headless Chromium for JavaScript-rendered pages
- **Multi-Format Data Processing**: 
  - PDF table extraction (pdfplumber)
  - CSV/Excel loading and cleaning (pandas)
  - HTML table parsing (BeautifulSoup4)
- **Smart Question Analysis**: Keyword detection for operations (sum, count, average, max, min, filter)
- **Automatic Answer Generation**:
  - Numeric answers (int, float)
  - Boolean answers (true/false)
  - Chart generation (Base64-encoded PNG via matplotlib)
  - JSON objects for complex answers
- **Quiz Chain Handling**: Automatically follows next_url to solve sequential quizzes
- **Background Processing**: Non-blocking async task execution
- **Robust Error Handling**: 3-minute timeout, 3-attempt retry logic, graceful fallbacks

### Production Features
- **Rate Limiting**: IP-based request throttling (configurable window & max)
- **Authentication**: Email + Secret validation
- **Health Monitoring**: `/` health check and `/info` diagnostics endpoints
- **Environment-Based Configuration**: Support for multiple deployment modes
- **Playwright Fallback**: Optional requests-only mode for restricted environments
- **Self-Ping**: Optional background task to prevent cold starts
- **Comprehensive Logging**: Detailed execution traces for debugging

---

## 🛠️ Tech Stack

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Backend** | Python | 3.10+ | Core runtime |
| **Web Framework** | FastAPI | 0.104.1 | API endpoints |
| **ASGI Server** | Uvicorn | 0.24.0 | Production server |
| **Browser Automation** | Playwright | 1.40.0 | JavaScript rendering |
| **Data Processing** | pandas | 2.1.3 | Data manipulation |
| **PDF Parsing** | pdfplumber | 0.10.3 | Table extraction |
| **Excel Support** | openpyxl | 3.1.2 | .xlsx files |
| **Web Scraping** | BeautifulSoup4 | 4.12.2 | HTML parsing |
| **Visualization** | matplotlib | 3.8.2 | Chart generation |
| **Visualization** | seaborn | 0.13.0 | Statistical plots |
| **HTTP Client** | requests | 2.31.0 | Answer submission |
| **Async HTTP** | aiohttp | 3.9.5 | Self-ping task |
| **Containerization** | Docker | - | Deployment |
| **Environment Config** | python-dotenv | 1.0.0 | .env support |

---

## 📋 Prerequisites

### Required
- **Python**: 3.10 or higher
- **pip**: Package installer for Python
- **Internet Connection**: For downloading files and submitting answers

### Optional (for development)
- **Docker**: For containerized deployment
- **Git**: For version control
- **Virtual Environment**: Recommended for isolation

### System Requirements
- **OS**: macOS, Linux, or Windows
- **RAM**: 2GB minimum (4GB recommended for Playwright)
- **Disk Space**: 500MB for dependencies + Chromium browser

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/udayprattap/quiz-solver.git
cd quiz-solver
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install Playwright Browsers

```bash
# Install Chromium browser for Playwright
playwright install chromium

# If you encounter permission issues on Linux:
playwright install --with-deps chromium
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Required
EMAIL=your.email@example.com
SECRET=your_secret_key

# Optional
PIPE_TOKEN=your_optional_api_token
DISABLE_PLAYWRIGHT=0
RATE_LIMIT_WINDOW=300
RATE_LIMIT_MAX=40
ENABLE_SELF_PING=0
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMAIL` | ✅ Yes | - | Your registered email address for authentication |
| `SECRET` | ✅ Yes | - | Secret key for request authorization |
| `PIPE_TOKEN` | ❌ No | - | External API bearer token (never logged) |
| `DISABLE_PLAYWRIGHT` | ❌ No | `0` | Set to `1` for requests-only fallback mode |
| `RATE_LIMIT_WINDOW` | ❌ No | `300` | Rate limit time window (seconds) |
| `RATE_LIMIT_MAX` | ❌ No | `40` | Max requests per IP per window |
| `ENABLE_SELF_PING` | ❌ No | `0` | Background self-ping to prevent cold starts |

### Configuration Scenarios

**Development (Local)**:
```env
EMAIL=your.email@example.com
SECRET=your_secret
DISABLE_PLAYWRIGHT=0
```

**Production (Docker)**:
```env
EMAIL=your.email@example.com
SECRET=your_secret
DISABLE_PLAYWRIGHT=0
RATE_LIMIT_WINDOW=300
RATE_LIMIT_MAX=40
```

**Restricted Environment (No Browser)**:
```env
EMAIL=your.email@example.com
SECRET=your_secret
DISABLE_PLAYWRIGHT=1
```

---

## 💻 Usage

### Starting the Server

#### Development Mode (with auto-reload)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Direct Python Execution

```bash
python main.py
```

The server will start at `http://localhost:8000`

### Making Requests

#### Health Check

```bash
curl http://localhost:8000/
```

**Expected Response:**
```json
{
  "status": "ready",
  "service": "TDS Quiz Solver",
  "version": "1.0.0",
  "timestamp": "2025-11-20T10:30:00.000000",
  "playwright_enabled": true,
  "rate_limit_window": 300,
  "rate_limit_max": 40
}
```

#### System Information

```bash
curl http://localhost:8000/info
```

#### Solve a Quiz

```bash
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your.email@example.com",
    "secret": "your_secret_key",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

**Expected Response:**
```json
{
  "status": "processing",
  "message": "Quiz solving started for URL: https://tds-llm-analysis.s-anand.net/demo"
}
```

---

## 📚 API Documentation

### Endpoints

#### `GET /`

Health check endpoint.

**Response: 200 OK**
```json
{
  "status": "ready",
  "service": "TDS Quiz Solver",
  "version": "1.0.0",
  "timestamp": "2025-11-20T10:30:00.000000",
  "playwright_enabled": true,
  "rate_limit_window": 300,
  "rate_limit_max": 40
}
```

---

#### `GET /info`

System information and configuration details.

**Response: 200 OK**
```json
{
  "settings": {
    "email": "your.email@example.com",
    "pipe_token_present": false
  },
  "playwright_enabled": true,
  "rate_limit": {
    "window_seconds": 300,
    "max_requests": 40
  }
}
```

---

#### `POST /solve`

Submit a quiz URL for automated solving.

**Request Body:**
```json
{
  "email": "your.email@example.com",
  "secret": "your_secret_key",
  "url": "https://quiz-url.com/start"
}
```

**Response: 200 OK** (Immediate)
```json
{
  "status": "processing",
  "message": "Quiz solving started for URL: https://quiz-url.com/start"
}
```

**Error Responses:**

- **403 Forbidden** - Invalid secret or email mismatch
```json
{
  "status": "error",
  "error": "Invalid secret key",
  "status_code": 403
}
```

- **429 Too Many Requests** - Rate limit exceeded
```json
{
  "status": "error",
  "error": "rate limit exceeded"
}
```

- **422 Unprocessable Entity** - Invalid request format
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

- **500 Internal Server Error** - Server error
```json
{
  "status": "error",
  "error": "Internal server error",
  "detail": "Error details here"
}
```

---

## 🧪 Testing

### Local Testing

#### 1. Start the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 2. Run Test Commands

```bash
# Test health check
curl http://localhost:8000/

# Test valid request
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your.email@example.com",
    "secret": "your_secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'

# Test invalid secret (should fail)
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your.email@example.com",
    "secret": "wrong_secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

#### 3. Monitor Logs

Watch the server terminal for output:
```
BACKGROUND TASK STARTED
Loading quiz page: https://...
Generated answer: 42
Submitting answer...
QUIZ CHAIN COMPLETED
```

### Production Testing

Use the included test script:

```bash
./test_production.sh
```

This runs a comprehensive test suite including:
- ✓ Health check
- ✓ Info endpoint
- ✓ Valid solve request
- ✓ Invalid secret rejection
- ✓ Invalid email rejection

---

## 🚢 Deployment

### Docker Deployment

#### Build the Image

```bash
docker build -t tds-quiz-solver .
```

#### Run the Container

```bash
docker run -d \
  -p 8000:8000 \
  -e EMAIL=your.email@example.com \
  -e SECRET=your_secret \
  tds-quiz-solver
```

#### Test the Container

```bash
curl http://localhost:8000/
```

---

### Hugging Face Spaces

**Live Deployment:** https://huggingface.co/spaces/udaypratap/quiz-solver

#### Setup Steps

1. **Create a Space**
   - Go to https://huggingface.co/spaces
   - Click "New Space"
   - Choose SDK: "Docker"
   - Name: `quiz-solver`

2. **Upload Files**
   - Upload all project files (see [Project Structure](#-project-structure))
   - Use `README_HF.md` as the Space README

3. **Configure Environment Variables**
   - Go to Space Settings → Variables & Secrets
   - Add:
     - `EMAIL` = your.email@example.com
     - `SECRET` = your_secret_key
     - `DISABLE_PLAYWRIGHT` = 0 (for Docker)
     - `RATE_LIMIT_WINDOW` = 300
     - `RATE_LIMIT_MAX` = 40

4. **Wait for Build** (2-5 minutes)
   - Docker container builds automatically
   - Monitor build logs for errors

5. **Test Deployment**
```bash
curl https://USERNAME-quiz-solver.hf.space/
```

---

### Render

1. **Push to GitHub** (already done)
2. **Connect Repository**
   - Go to https://render.com
   - New → Blueprint
   - Select your repository
3. **Configure**
   - Uses `render.yaml` for configuration
   - Add environment variables in Render dashboard
4. **Deploy**
   - Automatic deployment from main branch

---

### Cloud Run / Railway / Fly.io

See detailed instructions in `PROJECT_SUMMARY.md` for:
- Google Cloud Run deployment
- Railway quick start
- Fly.io configuration

---

## 🔧 Troubleshooting

### Common Issues

#### "playwright not found"

**Solution:**
```bash
pip install playwright
playwright install chromium
```

#### "ModuleNotFoundError: No module named 'pdfplumber'"

**Solution:**
```bash
pip install -r requirements.txt
```

#### "EMAIL or SECRET not set"

**Solution:**
Create a `.env` file:
```env
EMAIL=your.email@example.com
SECRET=your_secret_key
```

#### Server Not Responding

**Check if port 8000 is in use:**
```bash
# macOS/Linux
lsof -i :8000

# Windows
netstat -ano | findstr :8000
```

**Kill the process or use a different port:**
```bash
uvicorn main:app --port 8001
```

#### Quiz Times Out

**Causes:**
- Slow internet connection
- Quiz URL not accessible
- Complex JavaScript rendering

**Solutions:**
- Check internet connection
- Verify quiz URL in browser
- Increase timeout in `quiz_solver.py` (line 50)
- Check logs for specific errors

#### Playwright Browser Fails

**Linux users:**
```bash
# Install system dependencies
playwright install-deps

# Or use fallback mode
export DISABLE_PLAYWRIGHT=1
```

#### Docker Build Fails

**Check Python version in Dockerfile:**
```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy
```
Should use `jammy` (Python 3.10+), not `focal` (Python 3.8)

---

## 📁 Project Structure

```
quiz-solver/
├── app.py                  # Hugging Face Space entrypoint
├── main.py                 # FastAPI application & endpoints
├── quiz_solver.py          # Core quiz-solving logic
├── config.py               # Environment variable configuration
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker container configuration
├── .dockerignore           # Docker build exclusions
├── .env.example            # Environment template
├── .gitignore              # Git exclusions
├── README.md               # This file
├── README_HF.md            # Hugging Face Space README
├── PROJECT_SUMMARY.md      # Project overview & testing guide
├── test_production.sh      # Production test script
├── render.yaml             # Render deployment config
├── LICENSE                 # MIT License
└── utils/                  # Utility modules
    ├── __init__.py
    ├── pdf_processor.py    # PDF table extraction
    ├── csv_processor.py    # CSV/Excel data loading
    ├── web_scraper.py      # Web scraping utilities
    └── data_analyzer.py    # Data analysis functions
```

### Key Files

- **`main.py`**: FastAPI app, endpoints, background tasks, middleware
- **`quiz_solver.py`**: Quiz chain solving, question analysis, answer generation
- **`config.py`**: Credential validation, environment loading
- **`utils/`**: Modular utility functions for file processing and analysis

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 Uday Pratap

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

See the [LICENSE](LICENSE) file for full details.

---

## 📞 Contact

**Project Maintainer**: Uday Pratap

**GitHub Repository**: https://github.com/udayprattap/quiz-solver

**Hugging Face Space**: https://huggingface.co/spaces/udaypratap/quiz-solver

**Email**: 24ds3000019@ds.study.iitm.ac.in

### Support

For issues or questions:
1. Check [Troubleshooting](#-troubleshooting) section
2. Review server logs for detailed error messages
3. Verify all dependencies are installed correctly
4. Ensure `.env` file is configured properly
5. Test with the demo URL: `https://tds-llm-analysis.s-anand.net/demo`

---

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Playwright](https://playwright.dev/) - Browser automation
- [pandas](https://pandas.pydata.org/) - Data manipulation
- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF parsing
- [matplotlib](https://matplotlib.org/) - Data visualization
- [seaborn](https://seaborn.pydata.org/) - Statistical visualization

---

**Happy Quiz Solving! 🚀**
