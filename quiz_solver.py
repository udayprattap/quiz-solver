"""
Quiz Solver - Core Logic
Handles quiz chain solving with web scraping, file processing, and answer submission
"""

import asyncio
import re
import json
import base64
import os
from typing import Optional, Dict, Any, List
from io import BytesIO
import logging
from datetime import datetime

DISABLE_PLAYWRIGHT_ENV = os.getenv("DISABLE_PLAYWRIGHT", "0") == "1"
try:
    from playwright.async_api import async_playwright, Page  # type: ignore
except Exception:
    async_playwright = None  # type: ignore
    Page = Any  # type: ignore
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

# LLM integration for intelligent question analysis
try:
    from llm_helper import get_llm_analyzer
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

logger = logging.getLogger(__name__)


class QuizSolver:
    """
    Main class for solving TDS quiz challenges
    """
    
    def __init__(self, email: str, timeout: int = 180, disable_playwright: bool = False):
        """
        Initialize QuizSolver
        
        Args:
            email: User email for submissions
            timeout: Timeout per quiz in seconds (default 180)
        """
        self.email = email
        self.timeout = timeout
        self.browser: Optional[Any] = None
        self.disable_playwright = disable_playwright or DISABLE_PLAYWRIGHT_ENV
        
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
            if not self.disable_playwright and async_playwright is not None:
                async with async_playwright() as p:  # type: ignore
                    self.browser = await p.chromium.launch(headless=True)
                    chain_results = await self._solve_chain_loop(start_url)
                    if self.browser:
                        await self.browser.close()
                results.update(chain_results)
            else:
                chain_results = await self._solve_chain_loop_requests(start_url)
                results.update(chain_results)
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
        if self.disable_playwright:
            return await self.solve_single_quiz_requests(quiz_url)
        try:
            context = await self.browser.new_context()  # type: ignore
            page = await context.new_page()
            logger.info(f"Loading quiz page: {quiz_url}")
            await page.goto(quiz_url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(2)
            html = await page.content()
            text = await page.inner_text("body")
            logger.info(f"Page loaded. Text length: {len(text)}")
            result = await self.parse_and_solve(text, html, page)
            await context.close()
            return result
        except Exception as e:
            logger.error(f"Error solving single quiz: {e}")
            raise

    async def solve_single_quiz_requests(self, quiz_url: str) -> Dict[str, Any]:
        import requests
        logger.info(f"(Fallback) Fetching quiz page via requests: {quiz_url}")
        resp = requests.get(quiz_url, timeout=30)
        resp.raise_for_status()
        html = resp.text
        # crude text extraction
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        # Pass None for page (limited operations)
        result = await self.parse_and_solve(text, html, page=None)  # type: ignore
        return result

    async def _solve_chain_loop(self, start_url: str) -> Dict[str, Any]:
        results_partial = {"quizzes_solved": 0, "quizzes_failed": 0, "details": []}
        current_url = start_url
        quiz_number = 1
        while current_url:
            logger.info(f"\n{'='*60}\nSolving Quiz #{quiz_number}: {current_url}\n{'='*60}")
            try:
                result = await asyncio.wait_for(self.solve_single_quiz(current_url), timeout=self.timeout)
                results_partial["quizzes_solved"] += 1
                results_partial["details"].append({
                    "quiz_number": quiz_number,
                    "url": current_url,
                    "status": "success",
                    "answer": result.get("answer"),
                    "next_url": result.get("next_url")
                })
                current_url = result.get("next_url")
                if not current_url:
                    logger.info("Quiz chain completed!")
                    break
            except asyncio.TimeoutError:
                logger.error(f"Quiz #{quiz_number} timed out after {self.timeout} seconds")
                results_partial["quizzes_failed"] += 1
                results_partial["details"].append({
                    "quiz_number": quiz_number,
                    "url": current_url,
                    "status": "timeout"
                })
                break
            except Exception as e:
                logger.error(f"Error solving quiz #{quiz_number}: {e}")
                results_partial["quizzes_failed"] += 1
                results_partial["details"].append({
                    "quiz_number": quiz_number,
                    "url": current_url,
                    "status": "error",
                    "error": str(e)
                })
                break
            quiz_number += 1
        return results_partial

    async def _solve_chain_loop_requests(self, start_url: str) -> Dict[str, Any]:
        # identical logic using requests fallback
        return await self._solve_chain_loop(start_url)
    
    async def parse_and_solve(self, text: str, html: str, page: Optional[Any]) -> Dict[str, Any]:
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
    
    async def determine_answer(self, text: str, html: str, page: Optional[Any],
                               pdf_links: List[str], csv_links: List[str], 
                               excel_links: List[str]) -> Any:
        """
        Determine the answer based on question content
        
        Uses LLM (if available) for intelligent question understanding,
        with rule-based fallback for robustness.
        
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
        
        # Initialize LLM analyzer if available
        llm_analyzer = None
        if LLM_AVAILABLE:
            try:
                llm_analyzer = get_llm_analyzer()
                logger.info(f"🤖 LLM analyzer {'enabled' if llm_analyzer.enabled else 'disabled (fallback mode)'}")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM analyzer: {e}")
        
        # Load data if files are present
        df = None
        
        if csv_links and page is not None:
            # Get absolute URL
            csv_url = await self.get_absolute_url(page, csv_links[0])
            logger.info(f"Loading CSV: {csv_url}")
            df = load_data_from_url(csv_url)
            df = clean_data(df)
            
        elif excel_links and page is not None:
            excel_url = await self.get_absolute_url(page, excel_links[0])
            logger.info(f"Loading Excel: {excel_url}")
            df = load_data_from_url(excel_url)
            df = clean_data(df)
            
        elif pdf_links and page is not None:
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
            
            # Try LLM analysis first
            if llm_analyzer and llm_analyzer.enabled:
                try:
                    logger.info("🤖 Attempting LLM-powered question analysis...")
                    
                    data_info = {
                        "dataframe": df,
                        "columns": list(df.columns),
                        "shape": df.shape,
                        "data_source": "csv/excel/pdf"
                    }
                    
                    llm_result = await llm_analyzer.analyze_question(
                        question_text=text,
                        available_data=data_info,
                        html_content=html[:1000] if html else None
                    )
                    
                    if not llm_result.get("fallback_used"):
                        logger.info(f"✅ LLM analysis successful (confidence: {llm_result.get('confidence', 0):.2f})")
                        
                        # Try to execute LLM's suggested approach
                        llm_answer = await self._execute_llm_suggestion(df, llm_result)
                        if llm_answer is not None:
                            logger.info(f"✅ LLM-generated answer: {llm_answer}")
                            return llm_answer
                        else:
                            logger.info("⚠️  LLM suggestion execution failed, falling back to rules")
                    else:
                        logger.info("ℹ️  LLM requested fallback to rule-based logic")
                        
                except Exception as e:
                    logger.warning(f"⚠️  LLM analysis error: {e} - falling back to rule-based logic")
            
            # Fallback: Rule-based keyword matching (original logic)
            logger.info("📋 Using rule-based keyword matching...")
            
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
    
    async def _execute_llm_suggestion(self, df: pd.DataFrame, llm_result: Dict[str, Any]) -> Any:
        """
        Execute the operation suggested by LLM analysis
        
        Args:
            df: DataFrame to operate on
            llm_result: LLM analysis result
            
        Returns:
            Answer or None if execution fails
        """
        try:
            operation = llm_result.get("operation", "").lower()
            column = llm_result.get("column")
            filter_col = llm_result.get("filter_column")
            filter_val = llm_result.get("filter_value")
            
            # Apply filter if specified
            working_df = df
            if filter_col and filter_val and filter_col in df.columns:
                logger.info(f"Applying filter: {filter_col} == {filter_val}")
                working_df = df[df[filter_col] == filter_val]
            
            # Execute operation
            if operation == "sum" and column and column in working_df.columns:
                return int(working_df[column].sum())
            
            elif operation == "count":
                return int(len(working_df))
            
            elif operation == "mean" and column and column in working_df.columns:
                return float(working_df[column].mean())
            
            elif operation == "median" and column and column in working_df.columns:
                return float(working_df[column].median())
            
            elif operation == "max" and column and column in working_df.columns:
                return working_df[column].max()
            
            elif operation == "min" and column and column in working_df.columns:
                return working_df[column].min()
            
            elif operation == "chart":
                chart_type = llm_result.get("chart_type", "bar")
                return self.generate_chart(working_df, f"{chart_type} chart")
            
            elif operation == "boolean":
                # For true/false questions, use LLM's confidence
                confidence = llm_result.get("confidence", 0.5)
                return confidence > 0.6
            
            else:
                logger.warning(f"Unsupported LLM operation: {operation}")
                return None
                
        except Exception as e:
            logger.error(f"LLM suggestion execution failed: {e}")
            return None
    
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
    
    async def get_absolute_url(self, page: Any, url: str) -> str:
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
