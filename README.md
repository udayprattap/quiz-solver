# 🧠 TDS Quiz & Challenge Solver

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Unified solution for TDS LLM Analysis Challenges (Project 1 & Project 2)**

This repository contains automated solvers for:
1. **Project 1**: A webhook-based quiz solver using Playwright and GPT-4.
2. **Project 2**: A 21-stage multi-modal challenge solver (Audio, PDF, Images, CSV, etc.).

---

## 📑 Table of Contents

- [Project 2: Challenge Solver](#-project-2-challenge-solver)
- [Project 1: Quiz Webhook](#-project-1-quiz-webhook)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [License](#-license)

---

## 🏆 Project 2: Challenge Solver

A standalone async script (`project2_solver.py`) that solves the 21-stage TDS Project 2 challenge.

### Capabilities
- **Multi-Modal Processing**:
  - 🎙️ **Audio**: Transcribes WAV files using Google Speech Recognition.
  - 📄 **PDF**: Extracts tables and text using `pdfplumber`.
  - 🖼️ **Images**: Analyzes pixel data (heatmaps) using `Pillow`.
  - 📊 **Data**: Processes CSV/JSON logs using `pandas`.
- **Automated Workflow**:
  - Fetches questions from the challenge API.
  - Routes to specific solvers based on question type.
  - Submits answers and handles the challenge lifecycle.
- **Resilience**:
  - Handles rate limits and server errors.
  - Includes fallback logic for complex stages.

### Running the Solver

```bash
python project2_solver.py
```

The script will:
1. Authenticate using your `EMAIL` and `SECRET`.
2. Iterate through all 21 stages.
3. Print progress and results to the console.
4. Log detailed debug info to `solver.log`.

---

## 🌐 Project 1: Quiz Webhook

An intelligent webhook-based system that automatically receives quiz URLs, scrapes web pages, and submits answers.

### Features
- **Webhook Endpoint**: `/solve` endpoint for receiving quiz challenges.
- **Playwright Automation**: Headless browser for rendering quiz pages.
- **LLM Integration**: Uses GPT-4 for complex question analysis.
- **Production Ready**: Dockerized with rate limiting and keep-alive mechanisms.

### Running the Webhook

```bash
# Start the server
uvicorn main:app --host 0.0.0.0 --port 7860
```

Then send a POST request to `http://localhost:7860/solve`.

---

## 📋 Prerequisites

- **Python**: 3.10 or higher
- **FFmpeg**: Required for audio processing (Project 2).
  - macOS: `brew install ffmpeg`
  - Ubuntu: `sudo apt install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/)

---

## 🚀 Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/udayprattap/quiz-solver.git
   cd quiz-solver
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright Browsers** (for Project 1)
   ```bash
   playwright install chromium
   ```

---

## ⚙️ Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Required for both projects
EMAIL=your.email@example.com
SECRET=your_secret_key

# Optional
PIPE_TOKEN=your_openai_compatible_token
PORT=7860
```

---

## 📁 Project Structure

```
quiz-solver/
├── project2_solver.py      # MAIN: Project 2 Challenge Solver (21 Stages)
├── main.py                 # MAIN: Project 1 FastAPI Webhook
├── quiz_solver.py          # Project 1 Logic
├── config.py               # Centralized Configuration
├── requirements.txt        # Python Dependencies
├── Dockerfile              # Deployment Config
├── README.md               # Documentation
└── solver.log              # Execution Logs
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
