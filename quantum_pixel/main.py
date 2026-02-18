"""Run website as CLI."""

import os
import sys
import asyncio

import uvicorn
from . import FastAPIApp

async def test():
    """Open website and shutdown after 10s."""
    config = uvicorn.Config(FastAPIApp, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
    server = uvicorn.Server(config)

    # Run the server in a background task
    task = asyncio.create_task(server.serve())

    await asyncio.sleep(10)
    # Gracefully shut down the server
    await server.shutdown()
    await task

if __name__ == "__main__":
    if sys.argv[1] == "test":
        asyncio.run(test())
    else:
        uvicorn.run(FastAPIApp, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
