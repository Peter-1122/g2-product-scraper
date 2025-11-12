import json
import os
from typing import Any, List, Dict

class JsonWriter:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def write(self, items: List[Dict[str, Any]]) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)