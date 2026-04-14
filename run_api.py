"""Run the FastAPI backend. React frontend proxies /api to this server."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import uvicorn
from src.api.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
