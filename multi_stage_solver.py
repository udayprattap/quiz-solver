"""
Multi-Stage Quiz Challenge Solver
Automates the sequential quiz solving process by:
1. Fetching each stage URL
2. Extracting and solving the question
3. Submitting answer to /submit endpoint
4. Following the next URL chain
"""

import asyncio
import json
import logging
from typing import Dict, Optional, List, Any
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page

from config import EMAIL, SECRET, PIPE_TOKEN
from llm_helper import get_llm_analyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MultiStageSolver:
    """Solver for multi-stage quiz challenges"""
    
    def __init__(self):
        self.email = EMAIL
        self.secret = SECRET
        self.submit_url = "https://tds-llm-analysis.s-anand.net/submit"
        self.browser: Optional[Browser] = None
        self.llm_analyzer = get_llm_analyzer()
        self.results: List[Dict[str, Any]] = []
        
    async def initialize_browser(self):
        """Initialize Playwright browser"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        logger.info("Browser initialized")
    
    async def close_browser(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed")
    
    async def fetch_page_content(self, url: str) -> tuple[str, str]:
        """
        Fetch page content using Playwright for dynamic content
        Returns: (html_content, text_content)
        """
        logger.info(f"Fetching page: {url}")
        
        if not self.browser:
            await self.initialize_browser()
        
        page = await self.browser.new_page()
        
        try:
            # Navigate to page
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Wait a bit for any dynamic content
            await page.wait_for_timeout(2000)
            
            # Get HTML and text content
            html_content = await page.content()
            text_content = await page.evaluate("() => document.body.innerText")
            
            logger.info(f"Page fetched successfully. Content length: {len(text_content)}")
            return html_content, text_content
            
        except Exception as e:
            logger.error(f"Error fetching page: {e}")
            raise
        finally:
            await page.close()
    
    def extract_question_from_content(self, html: str, text: str) -> Dict[str, str]:
        """
        Extract question, instructions, and metadata from page content
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try to find structured content
        question_data = {
            'full_text': text,
            'html': html,
            'question': '',
            'instructions': '',
            'is_personalized': 'Not personalized' not in text,
            'difficulty': self._extract_difficulty(text)
        }
        
        # Look for common question patterns
        for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'div']):
            tag_text = tag.get_text(strip=True)
            if any(keyword in tag_text.lower() for keyword in ['question', 'task', 'what', 'how', 'find', 'calculate']):
                question_data['question'] = tag_text
                break
        
        # If no structured question found, use LLM to extract
        if not question_data['question']:
            question_data['question'] = text[:500]  # Use first 500 chars as context
        
        return question_data
    
    def _extract_difficulty(self, text: str) -> int:
        """Extract difficulty level from text"""
        import re
        match = re.search(r'difficulty[:\s]+(\d)', text.lower())
        return int(match.group(1)) if match else 1
    
    async def solve_question(self, question_data: Dict[str, str]) -> str:
        """
        Solve the question using LLM
        """
        logger.info("Solving question with LLM...")
        
        # Prepare context for LLM
        context = f"""
Question/Task: {question_data['question']}

Full Page Content:
{question_data['full_text'][:2000]}

Instructions:
- Extract the question clearly
- Provide a precise answer in the format requested
- If multiple choice, provide only the letter/option
- If numerical, provide only the number
- If text, provide concise answer
"""
        
        try:
            # Use LLM to analyze and solve
            answer = await self.llm_analyzer.analyze_question_async(
                question_text=context,
                options=[],  # No predefined options
                context=question_data['full_text'][:1000]
            )
            
            logger.info(f"LLM Answer: {answer}")
            return answer
            
        except Exception as e:
            logger.error(f"Error solving with LLM: {e}")
            # Fallback: Try to extract answer from page content
            return self._extract_answer_fallback(question_data)
    
    def _extract_answer_fallback(self, question_data: Dict[str, str]) -> str:
        """Fallback method to extract answer from page content"""
        text = question_data['full_text'].lower()
        
        # Look for common answer patterns
        import re
        
        # Pattern: "answer is X" or "the answer: X"
        answer_match = re.search(r'(?:answer|solution)(?:\s+is)?[\s:]+([^\n.]+)', text)
        if answer_match:
            return answer_match.group(1).strip()
        
        # If question asks for a number, try to find numbers
        if any(word in text for word in ['how many', 'count', 'number']):
            numbers = re.findall(r'\b\d+\b', text)
            if numbers:
                return numbers[0]
        
        # Default fallback
        return "Unable to determine answer automatically"
    
    async def submit_answer(self, url: str, answer: str) -> Dict[str, Any]:
        """
        Submit answer to the /submit endpoint
        Returns: Response JSON with status and next_url
        """
        logger.info(f"Submitting answer for URL: {url}")
        
        payload = {
            "email": self.email,
            "secret": self.secret,
            "url": url,
            "answer": answer
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    self.submit_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                result = response.json()
                logger.info(f"Submission response: {json.dumps(result, indent=2)}")
                
                return {
                    'status_code': response.status_code,
                    'response': result,
                    'success': response.status_code == 200
                }
                
            except Exception as e:
                logger.error(f"Error submitting answer: {e}")
                return {
                    'status_code': 500,
                    'response': {'error': str(e)},
                    'success': False
                }
    
    async def solve_stage(self, url: str) -> Dict[str, Any]:
        """
        Solve a single stage of the challenge
        Returns: Stage result with answer, submission response, and next_url
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"SOLVING STAGE: {url}")
        logger.info(f"{'='*60}\n")
        
        stage_result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'success': False
        }
        
        try:
            # Step 1: Fetch page content
            html, text = await self.fetch_page_content(url)
            
            # Step 2: Extract question
            question_data = self.extract_question_from_content(html, text)
            stage_result['question_data'] = question_data
            logger.info(f"Question extracted: {question_data['question'][:100]}...")
            
            # Step 3: Solve question
            answer = await self.solve_question(question_data)
            stage_result['answer'] = answer
            logger.info(f"Generated answer: {answer}")
            
            # Step 4: Submit answer
            submission = await self.submit_answer(url, answer)
            stage_result['submission'] = submission
            
            # Step 5: Extract next URL if available
            if submission['success'] and 'next' in submission['response']:
                stage_result['next_url'] = submission['response']['next']
                stage_result['success'] = True
            elif submission['success']:
                # Check for next_url or url field
                for field in ['next_url', 'url', 'nextUrl']:
                    if field in submission['response']:
                        stage_result['next_url'] = submission['response'][field]
                        stage_result['success'] = True
                        break
            
            return stage_result
            
        except Exception as e:
            logger.error(f"Error solving stage: {e}")
            stage_result['error'] = str(e)
            return stage_result
    
    async def solve_challenge(self, start_url: str, max_stages: int = 20) -> List[Dict[str, Any]]:
        """
        Solve the complete multi-stage challenge
        
        Args:
            start_url: Starting URL (e.g., project2)
            max_stages: Maximum number of stages to solve (safety limit)
        
        Returns: List of all stage results
        """
        logger.info(f"\n{'#'*60}")
        logger.info(f"STARTING MULTI-STAGE CHALLENGE")
        logger.info(f"Start URL: {start_url}")
        logger.info(f"{'#'*60}\n")
        
        current_url = start_url
        stage_count = 0
        
        try:
            await self.initialize_browser()
            
            while current_url and stage_count < max_stages:
                stage_count += 1
                logger.info(f"\n>>> Stage {stage_count}/{max_stages} <<<")
                
                # Solve current stage
                stage_result = await self.solve_stage(current_url)
                self.results.append(stage_result)
                
                # Check if we should continue
                if not stage_result.get('success'):
                    logger.warning("Stage failed or no next URL. Stopping.")
                    break
                
                # Get next URL
                next_url = stage_result.get('next_url')
                if not next_url:
                    logger.info("No more stages. Challenge complete!")
                    break
                
                current_url = next_url
                
                # Small delay between stages
                await asyncio.sleep(1)
            
            logger.info(f"\n{'#'*60}")
            logger.info(f"CHALLENGE COMPLETED")
            logger.info(f"Total stages solved: {stage_count}")
            logger.info(f"{'#'*60}\n")
            
            return self.results
            
        finally:
            await self.close_browser()
    
    def save_results(self, filename: str = "challenge_results.json"):
        """Save results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Results saved to {filename}")
    
    def print_summary(self):
        """Print summary of all stages"""
        print("\n" + "="*70)
        print("CHALLENGE SUMMARY")
        print("="*70 + "\n")
        
        for i, result in enumerate(self.results, 1):
            status = "✅ SUCCESS" if result.get('success') else "❌ FAILED"
            print(f"Stage {i}: {status}")
            print(f"  URL: {result['url']}")
            print(f"  Answer: {result.get('answer', 'N/A')}")
            
            if 'submission' in result:
                sub = result['submission']
                print(f"  Response: {sub.get('response', {}).get('message', 'N/A')}")
            
            print()


async def main():
    """Main entry point"""
    # Starting URL
    START_URL = "https://tds-llm-analysis.s-anand.net/project2"
    
    # Create solver
    solver = MultiStageSolver()
    
    try:
        # Solve the challenge
        results = await solver.solve_challenge(START_URL)
        
        # Save results
        solver.save_results()
        
        # Print summary
        solver.print_summary()
        
    except KeyboardInterrupt:
        logger.info("\nChallenge interrupted by user")
    except Exception as e:
        logger.error(f"Challenge failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
