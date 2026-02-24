"""Run website as CLI."""

import os

import uvicorn
from quantum_pixel import FastAPIApp

def main():
    """Run the web with script"""
    uvicorn.run(FastAPIApp, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

if __name__ == "__main__":
    main()
