import json
from typing import Any, Dict
import os

from jsonschema import Draft202012Validator, exceptions as js_exceptions

class SchemaValidator:
    def __init__(self, schema_path: str):
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema not found: {schema_path}")
        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)
        self.validator = Draft202012Validator(self.schema)

    def validate_instance(self, instance: Dict[str, Any]) -> None:
        errors = sorted(self.validator.iter_errors(instance), key=lambda e: e.path)
        if errors:
            first = errors[0]
            path = ".".join([str(p) for p in first.path]) or "<root>"
            raise js_exceptions.ValidationError(f"{path}: {first.message}")