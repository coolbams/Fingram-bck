from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "DATA_DIR"
DATA_DIR.mkdir(parents=True, exist_ok=True)

