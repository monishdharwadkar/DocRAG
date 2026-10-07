import sys
import os
from pathlib import Path

# api/index.py location: api/
api_dir = Path(__file__).resolve().parent
root_dir = api_dir.parent
backend_dir = root_dir / "backend"

# Ensure backend directory and root directory are in sys.path
for path_str in [str(backend_dir), str(root_dir)]:
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from app.main import app

# Vercel serverless application handler
