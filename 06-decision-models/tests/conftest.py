import sys
from pathlib import Path

BLOCK_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BLOCK_DIR))
