import argparse
import json
import logging
import os
import sys
import time
from typing import List, Dict, Any
from urllib.parse import urlparse

# Allow imports using the repo-relative paths even without packages
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, os.path.join(SRC_DIR, "extractors"))
sys.path.insert(0, os.path.join(SRC_DIR, "pipelines"))
sys.path.insert(0, os.path.join(SRC_DIR, "outputs"))

from extractors.product_profile import parse_product_profile  # type: ignore
from extractors.reviews_parser import parse_reviews           # type: ignore
from extractors.competitors import parse_competitive          # type: ignore
from extractors.pricing_parser import parse_pricing           # type: ignore
from pipelines.normalize import normalize_record              # type: ignore
from pipelines.validators import SchemaValidator              # type: ignore
from outputs.writer_json import JsonWriter                    # type: ignore

try:
    import requests
    from bs4 import BeautifulSoup
except Exception as e:  # pragma: no cover
    print("Missing dependencies. Run: pip install -r requirements.txt", file=sys.stderr)
    raise

DEFAULT_INPUTS = os.path.join(REPO_ROOT, "data", "inputs.sample.txt")
DEFAULT_OUTPUT = os.path.join(REPO_ROOT, "data", "sample_output.json")
DEFAULT_SETTINGS = os.path.join(SRC_DIR, "config", "settings.example.json")
DEFAULT_SCHEMA = os.path.join(SRC_DIR, "outputs", "schema.json")

logger = logging.getLogger("g2_scraper")

def load_settings(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def read_inputs(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

def fetch_html(source: str, timeout: int = 20) -> str:
    """
    Fetch HTML from a URL or read from a local file path.
    - If source starts with http/https, perform GET.
    - If source points to existing file, open and read.
    """
    parsed = urlparse(source)
    if parsed.scheme in ("http", "https"):
        resp = requests.get(source, timeout=timeout, headers={
            "User-Agent": "Mozilla/5.0 (compatible; G2ProductScraper/1.0; +https://bitbash.dev)"
        })
        resp.raise_for_status()
        return resp.text
    if os.path.exists(source):
        with open(source, "r", encoding="utf-8") as f:
            return f.read()
    raise FileNotFoundError(f"Cannot treat '{source}' as URL or file path")

def process_single(html: str, url: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    profile = parse_product_profile(soup, url=url)
    reviews = parse_reviews(soup, url=url)
    comp = parse_competitive(soup, url=url)
    pricing = parse_pricing(soup, url=url)

    record = {**profile, **comp, **pricing}
    record["initial_reviews"] = reviews.get("initial_reviews", [])
    return normalize_record(record)

def run(inputs: List[str], output_path: str, delay: float, schema_path: str) -> int:
    writer = JsonWriter(output_path)
    validator = SchemaValidator(schema_path)

    results: List[Dict[str, Any]] = []
    for i, src in enumerate(inputs, start=1):
        try:
            logger.info("Processing (%d/%d): %s", i, len(inputs), src)
            html = fetch_html(src)
            record = process_single(html, src)
            validator.validate_instance(record)
            results.append(record)
            if delay > 0 and i < len(inputs):
                time.sleep(delay)
        except Exception as e:
            logger.exception("Failed to process %s: %s", src, e)

    writer.write(results)
    logger.info("Wrote %d records -> %s", len(results), output_path)
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description="G2 Product Scraper - structured product data extractor")
    parser.add_argument("--inputs", default=DEFAULT_INPUTS, help="Path to file with URLs or local HTML paths (one per line)")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Path to write JSON output")
    parser.add_argument("--settings", default=DEFAULT_SETTINGS, help="Path to settings JSON")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA, help="Path to JSON schema")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests (seconds)")
    parser.add_argument("--log", default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR)")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if not os.path.exists(args.settings):
        logger.warning("Settings file not found at %s, using defaults.", args.settings)
        settings = {}
    else:
        settings = load_settings(args.settings)

    # Allow overriding delay from settings
    delay = settings.get("delay_seconds", args.delay)
    return run(read_inputs(args.inputs), args.output, delay, args.schema)

if __name__ == "__main__":
    sys.exit(main())