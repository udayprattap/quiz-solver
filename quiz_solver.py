"""
Quiz Solver - Core Logic
Handles quiz chain solving with web scraping, file processing, and answer submission
"""

import asyncio
import re
import json
import base64
from typing import Optional, Dict, Any, List
from io import BytesIO
import logging
from datetime import datetime

from playwright.async_api import async_playwright, Browser, Page
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

from utils.pdf_processor import download_pdf, extract_tables
from utils.csv_processor import load_data_from_url, clean_data
from utils.data_analyzer import (
    calculate_sum, count_rows, find_max_min, calculate_mean,
    calculate_median, value_counts, filter_dataframe
)

logger = logging.getLogger(__name__)


class QuizSolver:
    """
    Main class for solving TDS quiz challenges
    """
    
    def __init__(self, email: str, timeout: int = 180):
        """
        Initialize QuizSolver
        
        Args:
            email: User email for submissions
            timeout: Timeout per quiz in seconds (default 180)
        """
        self.email = email
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        
    async def solve_chain(self, start_url: str) -> Dict[str, Any]:
        """
        Solve the complete quiz chain starting from initial URL
        
        Args:
            start_url: Starting URL for quiz chain
            
        Returns:
            Dictionary with results and statistics
        """
        results = {
            "quizzes_solved": 0,
            "quizzes_failed": 0,
            "start_time": datetime.now().isoformat(),
            "details": []
        }
        
        try:
            async with async_playwright() as p:
                # Launch browser once for entire chain
                self.browser = await p.chromium.launch(headless=True)
                
                current_url = start_url
                quiz_number = 1
                
                while current_url:
                    logger.info(f"\n{'='*60}")
                    logger.info(f"Solving Quiz #{quiz_number}: {current_url}")
                    logger.info(f"{'='*60}\n")
                    
                    try:
                        # Solve single quiz with timeout
                        result = await asyncio.wait_for(
                            self.solve_single_quiz(current_url),
                            timeout=self.timeout
                        )
                        
                        results["quizzes_solved"] += 1
                        results["details"].append({
                            "quiz_number": quiz_number,
                            "url": current_url,
                            "status": "success",
                            "answer": result.get("answer"),
                            "next_url": result.get("next_url")
                        })
                        
                        # Get next URL
                        current_url = result.get("next_url")
                        
                        if not current_url:
                            logger.info("Quiz chain completed!")
                            break
                            
                    except asyncio.TimeoutError:
                        logger.error(f"Quiz #{quiz_number} timed out after {self.timeout} seconds")
                        results["quizzes_failed"] += 1
                        results["details"].append({
                            "quiz_number": quiz_number,
                            "url": current_url,
                            "status": "timeout"
                        })
                        break
                        
                    except Exception as e:
                        logger.error(f"Error solving quiz #{quiz_number}: {e}")
                        results["quizzes_failed"] += 1
                        results["details"].append({
                            "quiz_number": quiz_number,
                            "url": current_url,
                            "status": "error",
                            "error": str(e)
                        })
                        break
                    
                    quiz_number += 1
                
                await self.browser.close()
                
        except Exception as e:
            logger.error(f"Error in quiz chain: {e}")
            results["error"] = str(e)
        
        results["end_time"] = datetime.now().isoformat()
        return results
    
    async def solve_single_quiz(self, quiz_url: str) -> Dict[str, Any]:
        """
        Solve a single quiz
        
        Args:
            quiz_url: URL of the quiz
            
        Returns:
            Dictionary with answer and next URL
        """
        try:
            # Create new page
            context = await self.browser.new_context()
            page = await context.new_page()
            
            # Navigate to quiz page
            logger.info(f"Loading quiz page: {quiz_url}")
            await page.goto(quiz_url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(2)  # Wait for dynamic content
            
            # Extract page content
            html = await page.content()
            text = await page.inner_text("body")
            
            logger.info(f"Page loaded. Text length: {len(text)}")
            
            # Parse and solve the quiz
            result = await self.parse_and_solve(text, html, page)
            
            await context.close()
            
            return result
            
        except Exception as e:
            logger.error(f"Error solving single quiz: {e}")
            raise
    
    async def parse_and_solve(self, text: str, html: str, page: Page) -> Dict[str, Any]:
        """
        Parse quiz content and generate answer
        
        Args:
            text: Page text content
            html: Page HTML content
            page: Playwright page object
            
        Returns:
            Dictionary with answer and next URL
        """
        try:
            # Extract submit URL from HTML
            submit_url = self.extract_submit_url(html, text)
            logger.info(f"Submit URL: {submit_url}")
            
            # Check for Base64 encoded content
            if "atob(" in html or "base64" in text.lower():
                text = self.decode_base64_content(html)
                logger.info("Decoded Base64 content")
            
            # Find data files (PDF, CSV, Excel)
            pdf_links = re.findall(r'href="([^"]+\.pdf)"', html)
            csv_links = re.findall(r'href="([^"]+\.csv)"', html)
            excel_links = re.findall(r'href="([^"]+\.xlsx?)"', html)
            
            logger.info(f"Found files - PDFs: {len(pdf_links)}, CSVs: {len(csv_links)}, Excel: {len(excel_links)}")
            
            # Determine question type and solve
            answer = await self.determine_answer(text, html, page, pdf_links, csv_links, excel_links)
            
            logger.info(f"Generated answer: {answer}")
            
            # Submit answer
            next_url = await self.submit_answer(submit_url, answer)
            
            return {
                "answer": answer,
                "next_url": next_url,
                "submit_url": submit_url
            }
            
        except Exception as e:
            logger.error(f"Error parsing and solving: {e}")
            raise
    
    def extract_submit_url(self, html: str, text: str) -> str:
        """
        Extract submit URL from page
        
        Args:
            html: Page HTML
            text: Page text
            
        Returns:
            Submit URL
        """
        # Try different patterns
        patterns = [
            r'POST.*?(https://[^\s<>"]+/submit)',
            r'action="(https://[^"]+/submit)"',
            r'"submit":\s*"(https://[^"]+)"',
            r'submitUrl.*?(https://[^\s<>"]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html + text)
            if match:
                return match.group(1)
        
        # Try to find any submit-related URL
        match = re.search(r'(https://[^\s<>"]+submit[^\s<>"]*)', html + text)
        if match:
            return match.group(1)
        
        raise ValueError("Could not find submit URL")
    
    def decode_base64_content(self, html: str) -> str:
        """
        Decode Base64 encoded content from HTML
        
        Args:
            html: Page HTML
            
        Returns:
            Decoded text
        """
        try:
            # Find Base64 strings
            b64_pattern = r'atob\([\'"]([A-Za-z0-9+/=]+)[\'"]\)'
            matches = re.findall(b64_pattern, html)
            
            decoded_texts = []
            for b64_str in matches:
                try:
                    decoded = base64.b64decode(b64_str).decode('utf-8')
                    decoded_texts.append(decoded)
                except:
                    pass
            
            return "\n".join(decoded_texts)
            
        except Exception as e:
            logger.error(f"Error decoding Base64: {e}")
            return ""
    
    async def determine_answer(self, text: str, html: str, page: Page,
                               pdf_links: List[str], csv_links: List[str], 
                               excel_links: List[str]) -> Any:
        """
        Determine the answer based on question content
        
        Args:
            text: Question text
            html: Page HTML
            page: Playwright page
            pdf_links: List of PDF URLs
            csv_links: List of CSV URLs
            excel_links: List of Excel URLs
            
        Returns:
            Answer (can be int, float, str, bool, dict, or base64 image)
        """
        text_lower = text.lower()
        
        # Load data if files are present
        df = None
        
        if csv_links:
            # Get absolute URL
            csv_url = await self.get_absolute_url(page, csv_links[0])
            logger.info(f"Loading CSV: {csv_url}")
            df = load_data_from_url(csv_url)
            df = clean_data(df)
            
        elif excel_links:
            excel_url = await self.get_absolute_url(page, excel_links[0])
            logger.info(f"Loading Excel: {excel_url}")
            df = load_data_from_url(excel_url)
            df = clean_data(df)
            
        elif pdf_links:
            pdf_url = await self.get_absolute_url(page, pdf_links[0])
            logger.info(f"Loading PDF: {pdf_url}")
            pdf_path = download_pdf(pdf_url)
            
            # Check if specific page is mentioned
            page_match = re.search(r'page\s+(\d+)', text_lower)
            page_num = int(page_match.group(1)) if page_match else None
            
            tables = extract_tables(pdf_path, page_num)
            if tables:
                df = tables[0]  # Use first table
        
        # Analyze question and data
        if df is not None:
            logger.info(f"DataFrame loaded: {df.shape}")
            logger.info(f"Columns: {list(df.columns)}")
            
            # Determine operation based on keywords
            if any(keyword in text_lower for keyword in ['sum', 'total', 'add']):
                # Find numeric column
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    # Try to identify the right column from question
                    col = self.identify_column(text, df.columns)
                    if col and col in numeric_cols:
                        return int(calculate_sum(df, col))
                    else:
                        return int(calculate_sum(df, numeric_cols[0]))
            
            elif any(keyword in text_lower for keyword in ['count', 'how many', 'number of']):
                # Check for filtering condition
                filter_col = self.identify_column(text, df.columns)
                filter_val = self.identify_value(text, df, filter_col)
                
                if filter_col and filter_val:
                    condition = df[filter_col] == filter_val
                    return int(count_rows(df, condition))
                else:
                    return int(count_rows(df))
            
            elif any(keyword in text_lower for keyword in ['mean', 'average']):
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    col = self.identify_column(text, df.columns)
                    if col and col in numeric_cols:
                        return float(calculate_mean(df, col))
                    else:
                        return float(calculate_mean(df, numeric_cols[0]))
            
            elif any(keyword in text_lower for keyword in ['max', 'maximum', 'highest']):
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    col = self.identify_column(text, df.columns)
                    if col and col in numeric_cols:
                        result = find_max_min(df, col)
                        return result['max']
            
            elif any(keyword in text_lower for keyword in ['min', 'minimum', 'lowest']):
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    col = self.identify_column(text, df.columns)
                    if col and col in numeric_cols:
                        result = find_max_min(df, col)
                        return result['min']
        
        # Check for chart/plot questions
        if any(keyword in text_lower for keyword in ['chart', 'plot', 'graph', 'visualiz']):
            if df is not None:
                return self.generate_chart(df, text)
        
        # Boolean questions
        if any(keyword in text_lower for keyword in ['true or false', 'yes or no']):
            # Simple heuristic
            if any(word in text_lower for word in ['yes', 'true', 'correct']):
                return True
            else:
                return False
        
        # Default: return a simple answer
        # Try to extract number from text
        numbers = re.findall(r'\b\d+\.?\d*\b', text)
        if numbers:
            return int(float(numbers[0]))
        
        # Return string answer
        return "42"  # Default fallback
    
    def identify_column(self, text: str, columns: List[str]) -> Optional[str]:
        """
        Identify which column the question is asking about
        
        Args:
            text: Question text
            columns: DataFrame columns
            
        Returns:
            Column name or None
        """
        text_lower = text.lower()
        
        for col in columns:
            col_lower = str(col).lower()
            # Remove special characters for matching
            col_clean = re.sub(r'[^a-z0-9]', '', col_lower)
            
            if col_lower in text_lower or col_clean in text_lower.replace(' ', ''):
                return col
        
        return None
    
    def identify_value(self, text: str, df: pd.DataFrame, column: Optional[str]) -> Any:
        """
        Identify value to filter by from question text
        
        Args:
            text: Question text
            df: DataFrame
            column: Column name
            
        Returns:
            Value or None
        """
        if not column or column not in df.columns:
            return None
        
        # Get unique values in column
        unique_vals = df[column].unique()
        
        text_lower = text.lower()
        
        # Try to find matching value
        for val in unique_vals:
            val_str = str(val).lower()
            if val_str in text_lower:
                return val
        
        return None
    
    def generate_chart(self, df: pd.DataFrame, text: str) -> str:
        """
        Generate chart and return as Base64 PNG
        
        Args:
            df: DataFrame with data
            text: Question text describing chart
            
        Returns:
            Base64 encoded PNG image
        """
        try:
            plt.figure(figsize=(10, 6))
            
            # Determine chart type from question
            text_lower = text.lower()
            
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            if 'bar' in text_lower and len(df) < 50:
                # Bar chart
                if len(numeric_cols) > 0:
                    df.plot(kind='bar', x=df.columns[0], y=numeric_cols[0])
            
            elif 'line' in text_lower:
                # Line chart
                if len(numeric_cols) > 0:
                    df[numeric_cols[0]].plot(kind='line')
            
            elif 'scatter' in text_lower:
                # Scatter plot
                if len(numeric_cols) >= 2:
                    plt.scatter(df[numeric_cols[0]], df[numeric_cols[1]])
            
            else:
                # Default: histogram of first numeric column
                if len(numeric_cols) > 0:
                    df[numeric_cols[0]].hist(bins=20)
            
            plt.tight_layout()
            
            # Convert to Base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100)
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close()
            
            logger.info("Chart generated successfully")
            return img_base64
            
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            raise
    
    async def get_absolute_url(self, page: Page, url: str) -> str:
        """
        Convert relative URL to absolute URL
        
        Args:
            page: Playwright page
            url: Relative or absolute URL
            
        Returns:
            Absolute URL
        """
        if url.startswith('http'):
            return url
        
        # Use page.evaluate to get absolute URL
        abs_url = await page.evaluate(f'new URL("{url}", window.location.href).href')
        return abs_url
    
    async def submit_answer(self, submit_url: str, answer: Any, max_retries: int = 3) -> Optional[str]:
        """
        Submit answer to quiz endpoint
        
        Args:
            submit_url: URL to submit answer
            answer: Answer to submit
            max_retries: Maximum retry attempts
            
        Returns:
            Next quiz URL or None if chain is complete
        """
        import requests
        
        payload = {
            "email": self.email,
            "answer": answer
        }
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Submitting answer (attempt {attempt + 1}/{max_retries})")
                logger.info(f"Payload: {json.dumps(payload, indent=2)}")
                
                response = requests.post(
                    submit_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Check for next URL
                    next_url = result.get('next_url') or result.get('nextUrl') or result.get('next')
                    
                    if next_url:
                        logger.info(f"Next quiz URL: {next_url}")
                        return next_url
                    else:
                        logger.info("No next URL - quiz chain complete")
                        return None
                else:
                    logger.warning(f"Unexpected status code: {response.status_code}")
                    
                    # If we got a response, try to extract next URL anyway
                    try:
                        result = response.json()
                        next_url = result.get('next_url') or result.get('nextUrl') or result.get('next')
                        if next_url:
                            return next_url
                    except:
                        pass
                
                # Retry on failure
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error submitting answer: {e}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                else:
                    raise
        
        return None
