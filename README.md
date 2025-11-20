# TDS Quiz Solver - Automated Quiz-Solving System

Complete automated quiz-solving system for the TDS LLM Analysis challenge. This system receives quiz challenges via webhook, scrapes JavaScript-rendered web pages, processes files (PDF, CSV, Excel), analyzes data, and submits answers automatically within 3 minutes.

## Features

- ✅ FastAPI webhook endpoint for receiving quiz challenges
- ✅ Playwright headless browser for JavaScript-rendered pages
- ✅ PDF table extraction with pdfplumber
- ✅ CSV and Excel file processing with pandas
- ✅ Automated data analysis and answer generation
- ✅ Quiz chain solving (multiple quizzes in sequence)
- ✅ Background task processing
- ✅ Comprehensive error handling and logging
- ✅ Base64 content decoding
- ✅ Chart generation for visualization questions
- ✅ 3-minute timeout per quiz with retry logic

## Project Structure

```
tds-quiz-solver/
├── .env                    # Environment variables (EMAIL, SECRET)
├── .gitignore              # Git ignore file
├── main.py                 # FastAPI application with /solve endpoint
├── quiz_solver.py          # Core quiz-solving logic
├── requirements.txt        # Python dependencies
├── test_endpoint.py        # Testing script
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── pdf_processor.py    # PDF extraction
│   ├── csv_processor.py    # CSV/Excel handling
│   ├── web_scraper.py      # Web page scraping
│   └── data_analyzer.py    # Data processing
├── downloads/              # Temporary file storage
└── README.md              # This file
```

## Requirements

- Python 3.10 or higher
- Internet connection for downloading files and submitting answers
- macOS, Linux, or Windows

## Installation

### 1. Clone or Download the Project

```bash
cd tds-quiz-solver
```

### 2. Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers

```bash
playwright install chromium
```

This downloads the Chromium browser needed for web scraping.

### 5. Create Environment File

Create a `.env` file in the project root with your credentials:

```bash
EMAIL=your.email@example.com
SECRET=your_secret_key_here
# Optional external API token (leave blank if not needed)
PIPE_TOKEN=your_pipe_token_here
```

**Important:** Replace the values with your actual email and secret key. Leave `PIPE_TOKEN` only if you need authenticated outbound API calls; otherwise omit it.

The file `.env.example` contains a template. Never commit a real `PIPE_TOKEN`. It is treated like a password.

## Usage

### Starting the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Or run directly:

```bash
python main.py
```

The server will start on `http://localhost:8000`

### Testing the Endpoint

In a new terminal, run the test script:

```bash
python test_endpoint.py
```

This will run several tests:
1. ✅ Health check (`GET /`)
2. ✅ Valid request with demo URL
3. ✅ Invalid secret (should return 403)
4. ✅ Invalid JSON payload (should return 422)
5. ✅ Optional custom URL test

### Manual Testing with curl

Health check:
```bash
curl http://localhost:8000/
```

Submit a quiz:
```bash
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your.email@example.com",
    "secret": "your_secret_key",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

## API Endpoints

### GET /

Health check endpoint.

**Response:**
```json
{
  "status": "ready",
  "service": "TDS Quiz Solver",
  "version": "1.0.0",
  "timestamp": "2025-11-20T10:30:00.000000"
}
```

### POST /solve

Webhook endpoint to receive and solve quiz challenges.

**Request Body:**
```json
{
  "email": "your.email@example.com",
  "secret": "your_secret_key",
  "url": "https://quiz-url.com/start"
}
```

**Response (200 OK):**
```json
{
  "status": "processing",
  "message": "Quiz solving started for URL: https://quiz-url.com/start"
}
```

**Error Responses:**
- `403 Forbidden`: Invalid secret or email mismatch
- `422 Unprocessable Entity`: Invalid request payload
- `500 Internal Server Error`: Server error

## How It Works

1. **Webhook Receives Request**: FastAPI endpoint receives quiz URL and credentials
2. **Background Task Starts**: Quiz solving runs asynchronously to return immediate response
3. **Browser Automation**: Playwright opens the quiz page and waits for content to load
4. **Content Extraction**: Extracts HTML and text, decodes Base64 if present
5. **File Processing**: Downloads and processes PDF, CSV, or Excel files
6. **Data Analysis**: Analyzes data based on question keywords (sum, count, average, etc.)
7. **Answer Generation**: Generates appropriate answer type (int, float, bool, dict, or chart)
8. **Answer Submission**: Posts answer to submit endpoint with retry logic
9. **Chain Handling**: If next URL is provided, continues to next quiz
10. **Completion**: Logs results when chain is complete or timeout occurs

## Supported Question Types

- **Numeric**: Sum, total, count, average, mean, median, max, min
- **Boolean**: True/false, yes/no questions
- **Charts**: Bar charts, line plots, scatter plots, histograms (returned as Base64 PNG)
- **Complex**: JSON objects with multiple values

## Answer Detection Logic

The system analyzes question text to determine the appropriate answer:

- Keywords like "sum", "total" → Calculate sum of numeric column
- Keywords like "count", "how many" → Count rows (with optional filtering)
- Keywords like "mean", "average" → Calculate mean
- Keywords like "max", "highest" → Find maximum value
- Keywords like "min", "lowest" → Find minimum value
- Keywords like "chart", "plot" → Generate visualization as Base64 PNG
- Keywords like "true/false", "yes/no" → Return boolean

## File Support

- **PDF**: Extracts tables using pdfplumber, supports multi-page PDFs
- **CSV**: Loads directly from URL into pandas DataFrame
- **Excel**: Supports .xlsx and .xls formats
- **HTML Tables**: Parses tables from web pages

## Logging

The application logs all activities:

- Incoming requests and authentication
- Page loading and content extraction
- File downloads and processing
- Data analysis operations
- Answer generation and submission
- Quiz chain progress
- Errors and exceptions

Logs are printed to console with timestamps.

## Error Handling

- **Timeouts**: 3-minute limit per quiz
- **Network Errors**: Retry logic with 3 attempts
- **Invalid Data**: Graceful fallback to default answers
- **Missing Files**: Error logging and chain termination
- **Authentication**: Immediate rejection of invalid credentials

## Troubleshooting

### Issue: "playwright not found"
```bash
pip install playwright
playwright install chromium
```

### Issue: "ModuleNotFoundError: No module named 'pdfplumber'"
```bash
pip install -r requirements.txt
```

### Issue: "EMAIL or SECRET not set"
Create a `.env` file with:
```
EMAIL=your.email@example.com
SECRET=your_secret_key
```

### Issue: Server not responding
Check if port 8000 is available:
```bash
lsof -i :8000  # On macOS/Linux
netstat -ano | findstr :8000  # On Windows
```

### Issue: Quiz times out
- Check internet connection
- Verify the quiz URL is accessible
- Check logs for specific errors
- Increase timeout in `quiz_solver.py` if needed

## Development

### Adding New Analysis Functions

Add functions to `utils/data_analyzer.py`:

```python
def my_custom_analysis(df: pd.DataFrame, column: str) -> Any:
    """Your custom analysis logic"""
    result = df[column].my_operation()
    return result
```

Then use in `quiz_solver.py` in the `determine_answer` method.

### Adding New File Processors

Add processors to respective files in `utils/`:

```python
def process_new_format(url: str) -> pd.DataFrame:
    """Process new file format"""
    # Your processing logic
    return dataframe
```

## Performance

- Average quiz solving time: 30-60 seconds
- Timeout per quiz: 180 seconds (3 minutes)
- Maximum answer size: 1MB (per quiz requirements)
- Concurrent quizzes: Background tasks allow multiple simultaneous requests

## Security

- Environment variables for sensitive data (`EMAIL`, `SECRET`, optional `PIPE_TOKEN`)
- Secret key validation on all requests
- Email matching verification
- Token redaction: application logs only whether `PIPE_TOKEN` is set, never the full value
- No credentials or raw tokens in responses
- HTTPS support for production deployment

### Using PIPE_TOKEN (Optional)

If you need to call an external API requiring bearer authentication:

```python
from config import get_pipe_token
token = get_pipe_token()
if token:
  headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
```

If `PIPE_TOKEN` is absent, code should gracefully skip authenticated requests.

## Production Deployment

For production, consider:

1. Use a production ASGI server (uvicorn with workers)
2. Set up HTTPS with SSL certificates
3. Use environment variables or secrets management
4. Configure logging to files or log aggregation service
5. Set up monitoring and alerting
6. Use a process manager (systemd, supervisor, or Docker)

Example production command:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## License

This project is for educational purposes as part of the TDS LLM Analysis challenge.

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Verify all dependencies are installed correctly
3. Ensure `.env` file is configured properly
4. Test with the demo URL first: `https://tds-llm-analysis.s-anand.net/demo`

## Credits

Built with:
- FastAPI
- Playwright
- pandas
- pdfplumber
- matplotlib
- seaborn

---

**Happy Quiz Solving! 🚀**
