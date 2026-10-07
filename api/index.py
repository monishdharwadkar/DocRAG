import sys
import os
from pathlib import Path

# Add project root and backend to python path for Vercel Serverless Execution
root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"

sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(backend_dir))

from app.main import app

# Vercel entry point
