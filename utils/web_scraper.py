"""
Web Scraping Utilities
Handles JavaScript-rendered pages using Playwright
"""

import asyncio
from playwright.async_api import async_playwright, Page, Browser
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


async def scrape_page(url: str, wait_time: int = 5) -> Dict[str, str]:
    """
    Scrape a JavaScript-rendered page using Playwright
    
    Args:
        url: URL to scrape
        wait_time: Time to wait for page load (seconds)
        
    Returns:
        Dictionary with 'html' and 'text' content
    """
    try:
        logger.info(f"Scraping page: {url}")
        
        async with async_playwright() as p:
            # Launch browser in headless mode
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            # Navigate to URL and wait for network to be idle
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Additional wait for dynamic content
            await asyncio.sleep(wait_time)
            
            # Extract HTML and text content
            html = await page.content()
            text = await page.inner_text("body")
            
            await browser.close()
            
            logger.info(f"Page scraped successfully: {len(html)} chars HTML, {len(text)} chars text")
            
            return {
                "html": html,
                "text": text
            }
            
    except Exception as e:
        logger.error(f"Error scraping page: {e}")
        raise


def extract_links(html: str) -> List[str]:
    """
    Extract all href links from HTML
    
    Args:
        html: HTML content
        
    Returns:
        List of URLs
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            links.append(href)
        
        logger.info(f"Extracted {len(links)} links")
        return links
        
    except Exception as e:
        logger.error(f"Error extracting links: {e}")
        return []


def extract_tables(html: str) -> List[pd.DataFrame]:
    """
    Extract HTML tables and convert to pandas DataFrames
    
    Args:
        html: HTML content
        
    Returns:
        List of pandas DataFrames
    """
    try:
        # Use pandas to read HTML tables
        tables = pd.read_html(html)
        logger.info(f"Extracted {len(tables)} HTML tables")
        return tables
        
    except Exception as e:
        logger.error(f"Error extracting tables: {e}")
        return []


async def get_page_with_browser(url: str, browser: Browser, wait_time: int = 5) -> Dict[str, any]:
    """
    Scrape page using existing browser instance
    
    Args:
        url: URL to scrape
        browser: Playwright browser instance
        wait_time: Time to wait for page load
        
    Returns:
        Dictionary with page content and page object
    """
    try:
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(wait_time)
        
        html = await page.content()
        text = await page.inner_text("body")
        
        return {
            "html": html,
            "text": text,
            "page": page,
            "context": context
        }
        
    except Exception as e:
        logger.error(f"Error getting page: {e}")
        raise


async def scrape_with_actions(url: str, actions: List[Dict]) -> Dict[str, str]:
    """
    Scrape page and perform actions (click, type, etc.)
    
    Args:
        url: URL to scrape
        actions: List of actions to perform
                 Each action is a dict with 'type' and parameters
                 
    Returns:
        Dictionary with final page content
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Perform actions
            for action in actions:
                action_type = action.get('type')
                
                if action_type == 'click':
                    selector = action.get('selector')
                    await page.click(selector)
                    await asyncio.sleep(1)
                    
                elif action_type == 'type':
                    selector = action.get('selector')
                    text = action.get('text')
                    await page.type(selector, text)
                    
                elif action_type == 'wait':
                    time = action.get('time', 1)
                    await asyncio.sleep(time)
            
            # Get final content
            html = await page.content()
            text = await page.inner_text("body")
            
            await browser.close()
            
            return {
                "html": html,
                "text": text
            }
            
    except Exception as e:
        logger.error(f"Error scraping with actions: {e}")
        raise
