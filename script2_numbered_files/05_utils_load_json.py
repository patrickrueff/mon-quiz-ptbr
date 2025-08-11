import json
from pathlib import Path

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))
