"""Run FastAPI app with an ngrok tunnel.

Usage:
    python run_with_ngrok.py --port 8000 --authtoken <YOUR_NGROK_TOKEN>

If authtoken is already added via `ngrok config add-authtoken`, you can omit it.
This script:
1. Starts uvicorn server programmatically.
2. Creates an ngrok tunnel to the specified port.
3. Prints the public URL for /solve and / endpoints.
4. Keeps running until interrupted (Ctrl+C).

Evaluation window reliability notes:
- Free ngrok sessions last up to 2 hours; your 1-hour window fits.
- Start this 10–15 minutes before the window: ~2:45 PM IST (Asia/Kolkata).
- If tunnel drops, restart the script.
"""

import argparse
import asyncio
import signal
import sys
import threading
import time
from typing import Optional

from pyngrok import ngrok, conf
import uvicorn

NGROK_REGION = "in"  # Use India region for lower latency, fallback to nearest if unsupported.


def start_uvicorn(host: str, port: int):
    """Start uvicorn in the current thread (blocking)."""
    uvicorn.run("main:app", host=host, port=port, log_level="info")


def create_tunnel(port: int, authtoken: Optional[str] = None) -> str:
    """Create ngrok tunnel and return public URL."""
    if authtoken:
        conf.get_default().auth_token = authtoken
    # Open HTTP tunnel
    tunnel = ngrok.connect(addr=port, proto="http", region=NGROK_REGION)
    return tunnel.public_url


def graceful_shutdown(tunnel_url: str):
    print("\nShutting down... Closing ngrok tunnel.")
    try:
        ngrok.disconnect(tunnel_url)
        ngrok.kill()
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="Run FastAPI with ngrok tunnel")
    parser.add_argument("--port", type=int, default=8000, help="Local port to expose")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host binding")
    parser.add_argument("--authtoken", type=str, default=None, help="Optional ngrok authtoken")
    args = parser.parse_args()

    # Start uvicorn in a thread so we can run ngrok and handle signals
    server_thread = threading.Thread(target=start_uvicorn, args=(args.host, args.port), daemon=True)
    server_thread.start()

    # Wait briefly for server to start
    time.sleep(2)

    try:
        public_url = create_tunnel(args.port, args.authtoken)
    except Exception as e:
        print(f"Error creating ngrok tunnel: {e}")
        print("Ensure ngrok is installed or pyngrok has access to authtoken.")
        print("Get token: https://dashboard.ngrok.com/get-started/your-authtoken")
        sys.exit(1)

    solve_endpoint = f"{public_url}/solve"
    health_endpoint = f"{public_url}/"

    print("\n=== NGROK TUNNEL ACTIVE ===")
    print(f"Public Base URL: {public_url}")
    print(f"Health Check:    {health_endpoint}")
    print(f"Solve Endpoint:  {solve_endpoint}")
    print("================================")
    print("Press Ctrl+C to stop.")

    # Periodic heartbeat
    try:
        while server_thread.is_alive():
            time.sleep(30)
    except KeyboardInterrupt:
        graceful_shutdown(public_url)


if __name__ == "__main__":
    main()
