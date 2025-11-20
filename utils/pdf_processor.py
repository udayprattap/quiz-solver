"""
PDF Processing Utilities
Handles PDF download and table extraction using pdfplumber
"""

import os
import requests
import pdfplumber
import pandas as pd
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


def download_pdf(url: str, save_dir: str = "downloads") -> str:
    """
    Download PDF from URL to local directory
    
    Args:
        url: PDF file URL
        save_dir: Directory to save the file
        
    Returns:
        Path to downloaded PDF file
    """
    try:
        # Ensure download directory exists
        os.makedirs(save_dir, exist_ok=True)
        
        # Extract filename from URL
        filename = url.split("/")[-1]
        if not filename.endswith(".pdf"):
            filename = "document.pdf"
        
        filepath = os.path.join(save_dir, filename)
        
        # Download file
        logger.info(f"Downloading PDF from {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Save to file
        with open(filepath, "wb") as f:
            f.write(response.content)
        
        logger.info(f"PDF saved to {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error downloading PDF: {e}")
        raise


def extract_tables(pdf_path: str, page_num: Optional[int] = None) -> List[pd.DataFrame]:
    """
    Extract tables from PDF using pdfplumber
    
    Args:
        pdf_path: Path to PDF file
        page_num: Specific page number (1-indexed), or None for all pages
        
    Returns:
        List of pandas DataFrames containing extracted tables
    """
    try:
        tables = []
        
        with pdfplumber.open(pdf_path) as pdf:
            # Determine which pages to process
            if page_num is not None:
                # Convert to 0-indexed
                pages_to_process = [pdf.pages[page_num - 1]]
                logger.info(f"Extracting tables from page {page_num}")
            else:
                pages_to_process = pdf.pages
                logger.info(f"Extracting tables from all {len(pdf.pages)} pages")
            
            # Extract tables from each page
            for page_idx, page in enumerate(pages_to_process):
                page_tables = page.extract_tables()
                
                if page_tables:
                    for table_idx, table in enumerate(page_tables):
                        if table and len(table) > 0:
                            # Convert to DataFrame
                            # First row is typically headers
                            if len(table) > 1:
                                df = pd.DataFrame(table[1:], columns=table[0])
                            else:
                                df = pd.DataFrame(table)
                            
                            # Clean column names
                            df.columns = [str(col).strip() if col else f"Column_{i}" 
                                         for i, col in enumerate(df.columns)]
                            
                            # Remove empty rows
                            df = df.dropna(how='all')
                            
                            tables.append(df)
                            logger.info(f"Extracted table {table_idx + 1} from page {page_idx + 1}: {df.shape}")
        
        if not tables:
            logger.warning("No tables found in PDF")
        else:
            logger.info(f"Total tables extracted: {len(tables)}")
        
        return tables
        
    except Exception as e:
        logger.error(f"Error extracting tables from PDF: {e}")
        raise


def extract_all_text(pdf_path: str, page_num: Optional[int] = None) -> str:
    """
    Extract all text from PDF
    
    Args:
        pdf_path: Path to PDF file
        page_num: Specific page number (1-indexed), or None for all pages
        
    Returns:
        Extracted text as string
    """
    try:
        text = []
        
        with pdfplumber.open(pdf_path) as pdf:
            if page_num is not None:
                pages_to_process = [pdf.pages[page_num - 1]]
            else:
                pages_to_process = pdf.pages
            
            for page in pages_to_process:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        
        return "\n".join(text)
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise
