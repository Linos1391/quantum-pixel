"""Run website as CLI."""

import os

import uvicorn
from . import FastAPIApp

uvicorn.run(FastAPIApp, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
