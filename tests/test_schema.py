import json
import os
import sys
from jsonschema import Draft202012Validator

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
SCHEMA = os.path.join(SRC, "outputs", "schema.json")
SAMPLE = os.path.join(ROOT, "data", "sample_output.json")

def test_sample_output_matches_schema():
    with open(SCHEMA, "r", encoding="utf-8") as f:
        schema = json.load(f)
    with open(SAMPLE, "r", encoding="utf-8") as f:
        data = json.load(f)
    validator = Draft202012Validator(schema)
    # Validate every record in sample output
    for rec in data:
        errors = sorted(validator.iter_errors(rec), key=lambda e: e.path)
        assert not errors, f"Schema validation errors: {errors}"