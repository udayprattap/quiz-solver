"""
FastAPI Application - TDS Quiz Solver Webhook Endpoint
"""

import os
import asyncio
from typing import Dict, Any
from datetime import datetime
import logging

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from quiz_solver import QuizSolver

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get credentials from environment
EMAIL = os.getenv("EMAIL")
SECRET = os.getenv("SECRET")

if not EMAIL or not SECRET:
    logger.error("EMAIL and SECRET must be set in .env file")
    raise ValueError("EMAIL and SECRET environment variables are required")

# Create FastAPI app
app = FastAPI(
    title="TDS Quiz Solver",
    description="Automated quiz-solving system for TDS LLM Analysis challenge",
    version="1.0.0"
)


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
        "timestamp": datetime.now().isoformat()
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
        solver = QuizSolver(email=email, timeout=180)
        
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


@app.on_event("startup")
async def startup_event():
    """
    Run on application startup
    """
    logger.info("="*70)
    logger.info("TDS Quiz Solver API Starting")
    logger.info(f"Email: {EMAIL}")
    logger.info("="*70)


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
