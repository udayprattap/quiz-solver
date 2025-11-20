"""
FastAPI Application - TDS Quiz Solver Webhook Endpoint
"""

import os
import asyncio
from typing import Dict, Any
from datetime import datetime
import logging
import httpx

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from quiz_solver import QuizSolver
from config import EMAIL, SECRET, get_pipe_token, validate_core_credentials, settings_summary

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate mandatory credentials
try:
    validate_core_credentials()
except ValueError as cred_err:
    logger.error(str(cred_err))
    raise

# Optional PIPE token presence (never log full token)
PIPE_TOKEN_PRESENT = bool(get_pipe_token())
if PIPE_TOKEN_PRESENT:
    logger.info("PIPE_TOKEN detected (redacted)")
else:
    logger.info("PIPE_TOKEN not set; continuing without external API token")

# Create FastAPI app
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "300"))  # seconds
RATE_LIMIT_MAX = int(os.getenv("RATE_LIMIT_MAX", "40"))  # requests per window per IP
DISABLE_PLAYWRIGHT = os.getenv("DISABLE_PLAYWRIGHT", "0") == "1"
ENABLE_KEEP_ALIVE = os.getenv("ENABLE_KEEP_ALIVE", "1") == "1"  # Keep service awake

_request_counts: Dict[str, Dict[str, Any]] = {}
_keep_alive_task = None

app = FastAPI(
    title="TDS Quiz Solver",
    description="Automated quiz-solving system for TDS LLM Analysis challenge",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    ip = request.client.host if request.client else "unknown"
    now = datetime.utcnow().timestamp()
    bucket = _request_counts.get(ip)
    if not bucket or now - bucket["start"] > RATE_LIMIT_WINDOW:
        bucket = {"start": now, "count": 0}
        _request_counts[ip] = bucket
    bucket["count"] += 1
    if bucket["count"] > RATE_LIMIT_MAX:
        return JSONResponse(status_code=429, content={"status": "error", "error": "rate limit exceeded"})
    return await call_next(request)


class QuizRequest(BaseModel):
    """Request model for quiz solving"""
    email: str = Field(..., description="User email address")
    secret: str = Field(..., description="Secret key for authentication")
    url: str = Field(..., description="Starting URL for quiz chain")


class QuizResponse(BaseModel):
    """Response model for quiz solving"""
    status: str = Field(..., description="Processing status")
    message: str = Field(default="", description="Additional message")


@app.get("/")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        Status information
    """
    return {
        "status": "ready",
        "service": "TDS Quiz Solver",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "playwright_enabled": not DISABLE_PLAYWRIGHT,
        "rate_limit_window": RATE_LIMIT_WINDOW,
        "rate_limit_max": RATE_LIMIT_MAX
    }


@app.get("/info")
async def info():
    return {
        "settings": settings_summary(),
        "playwright_enabled": not DISABLE_PLAYWRIGHT,
        "rate_limit": {
            "window_seconds": RATE_LIMIT_WINDOW,
            "max_requests": RATE_LIMIT_MAX
        }
    }


@app.post("/solve", response_model=QuizResponse)
async def solve_quiz(
    request: QuizRequest,
    background_tasks: BackgroundTasks,
    raw_request: Request
):
    """
    Webhook endpoint to receive and solve quiz challenges
    
    Args:
        request: Quiz request with email, secret, and URL
        background_tasks: FastAPI background tasks
        raw_request: Raw request object for logging
        
    Returns:
        Immediate response with processing status
    """
    try:
        # Log incoming request
        logger.info(f"Received quiz request from {request.email}")
        logger.info(f"Quiz URL: {request.url}")
        
        # Validate secret
        if request.secret != SECRET:
            logger.warning(f"Invalid secret provided by {request.email}")
            raise HTTPException(
                status_code=403,
                detail="Invalid secret key"
            )
        
        # Verify email matches
        if request.email != EMAIL:
            logger.warning(f"Email mismatch: {request.email} != {EMAIL}")
            raise HTTPException(
                status_code=403,
                detail="Email does not match configured user"
            )
        
        # Add quiz solving to background tasks
        background_tasks.add_task(
            solve_quiz_background,
            request.email,
            request.url
        )
        
        logger.info(f"Quiz solving task started in background for {request.url}")
        
        # Return immediate response
        return QuizResponse(
            status="processing",
            message=f"Quiz solving started for URL: {request.url}"
        )
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Error processing quiz request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


async def solve_quiz_background(email: str, start_url: str):
    """
    Background task to solve quiz chain
    
    Args:
        email: User email
        start_url: Starting quiz URL
    """
    try:
        logger.info(f"\n{'='*70}")
        logger.info(f"BACKGROUND TASK STARTED")
        logger.info(f"Email: {email}")
        logger.info(f"Start URL: {start_url}")
        logger.info(f"{'='*70}\n")
        
        # Create solver instance
        solver = QuizSolver(email=email, timeout=180, disable_playwright=DISABLE_PLAYWRIGHT)
        
        # Solve the quiz chain
        results = await solver.solve_chain(start_url)
        
        # Log results
        logger.info(f"\n{'='*70}")
        logger.info(f"QUIZ CHAIN COMPLETED")
        logger.info(f"Quizzes solved: {results['quizzes_solved']}")
        logger.info(f"Quizzes failed: {results['quizzes_failed']}")
        logger.info(f"Start time: {results['start_time']}")
        logger.info(f"End time: {results['end_time']}")
        logger.info(f"{'='*70}\n")
        
        # Log individual quiz results
        for detail in results['details']:
            logger.info(f"Quiz #{detail['quiz_number']}: {detail['status']}")
            if detail.get('answer'):
                logger.info(f"  Answer: {detail['answer']}")
            if detail.get('error'):
                logger.info(f"  Error: {detail['error']}")
        
    except Exception as e:
        logger.error(f"Error in background task: {e}", exc_info=True)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom exception handler for HTTP exceptions
    
    Args:
        request: Request object
        exc: HTTP exception
        
    Returns:
        JSON response with error details
    """
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Custom exception handler for general exceptions
    
    Args:
        request: Request object
        exc: Exception
        
    Returns:
        JSON response with error details
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


async def keep_alive_ping():
    """
    Keep service awake by self-pinging every 10 minutes
    Prevents Render free tier from sleeping during evaluation
    """
    await asyncio.sleep(60)  # Wait 1 minute after startup
    
    port = int(os.getenv("PORT", "7860"))
    while True:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.get(f"http://localhost:{port}/")
                logger.info("✓ Keep-alive ping successful")
        except Exception as e:
            logger.warning(f"Keep-alive ping failed: {e}")
        
        await asyncio.sleep(600)  # Ping every 10 minutes


@app.on_event("startup")
async def startup_event():
    """
    Run on application startup
    """
    global _keep_alive_task
    
    logger.info("="*70)
    logger.info("TDS Quiz Solver API Starting")
    logger.info(f"Email configured: {EMAIL}")
    logger.info(f"Settings summary: {settings_summary()}")
    logger.info("="*70)
    
    # Start keep-alive task if enabled (default: enabled on Render)
    if ENABLE_KEEP_ALIVE:
        _keep_alive_task = asyncio.create_task(keep_alive_ping())
        logger.info("✓ Keep-alive mechanism ENABLED (10-minute intervals)")
    else:
        logger.info("Keep-alive mechanism DISABLED")
    
    # Legacy self-ping support
    async def self_ping():
        import aiohttp
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    await session.get("http://localhost:8000/")
            except Exception:
                pass
            await asyncio.sleep(120)  # every 2 minutes
    if os.getenv("ENABLE_SELF_PING", "0") == "1":
        asyncio.create_task(self_ping())


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown
    """
    logger.info("TDS Quiz Solver API Shutting Down")


if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
