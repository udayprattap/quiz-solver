"""Hugging Face Spaces entrypoint.

Spaces (Python backend) looks for a variable named `app`.
We import the FastAPI instance from main.py.

IMPORTANT: HF Spaces expects the app to run on port 7860.
The Dockerfile is configured to use PORT environment variable.

Playwright caveat: The default Spaces CPU image may lack system
libraries for Chromium. We use Docker Space with Playwright pre-installed.
"""

import os
from main import app  # re-export FastAPI app

# Verify port configuration for HF Spaces
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
