"""
Utility modules for TDS Quiz Solver
"""

from .pdf_processor import download_pdf, extract_tables
from .csv_processor import load_csv, load_excel, clean_data
from .web_scraper import scrape_page, extract_links, extract_tables as extract_html_tables
from .data_analyzer import calculate_sum, count_rows, aggregate_stats, find_max_min

__all__ = [
    'download_pdf',
    'extract_tables',
    'load_csv',
    'load_excel',
    'clean_data',
    'scrape_page',
    'extract_links',
    'extract_html_tables',
    'calculate_sum',
    'count_rows',
    'aggregate_stats',
    'find_max_min'
]
