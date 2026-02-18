"""Run website as CLI."""

import uvicorn
from . import FastAPIApp

uvicorn.run(FastAPIApp)
