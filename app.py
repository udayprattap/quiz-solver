"""Hugging Face Spaces entrypoint.

Spaces (Python backend) looks for a variable named `app`.
We import the FastAPI instance from main.py. Adjust PORT by setting
`PORT=7860` in the Space settings if desired; default is 8000.

Playwright caveat: The default Spaces CPU image may lack system
libraries for Chromium. Prefer Docker Space using our provided Dockerfile
OR disable Playwright features if scraping not required in demo.
"""

from main import app  # re-export FastAPI app
