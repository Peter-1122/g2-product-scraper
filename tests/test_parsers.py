import os
import sys
from bs4 import BeautifulSoup

# Make src importable without packages
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)
sys.path.insert(0, os.path.join(SRC, "extractors"))
sys.path.insert(0, os.path.join(SRC, "pipelines"))

from extractors.product_profile import parse_product_profile  # type: ignore
from extractors.reviews_parser import parse_reviews           # type: ignore
from extractors.competitors import parse_competitive          # type: ignore
from extractors.pricing_parser import parse_pricing           # type: ignore
from pipelines.normalize import normalize_record              # type: ignore

HTML = """
<html>
  <body>
    <h1 data-testid="product-profile-header">Acme Widget</h1>
    <div data-testid="what-is"><p>Acme makes widgets for teams.</p></div>
    <div><span data-testid="average-rating">4.7</span></div>
    <div data-testid="review-count">1,234</div>

    <a href="https://www.g2.com/categories/widget-tools">Widget Tools</a>

    <div class="pricing">
      <div class="plan">
        <h3>Starter</h3>
        <p>Good for small teams</p>
        <ul><li>Feature A</li><li>Feature B</li></ul>
      </div>
    </div>

    <a href="https://www.g2.com/products/contoso/reviews">Contoso</a>
    <a href="https://www.g2.com/compare/acme-vs-contoso">Compare Acme vs Contoso</a>

    <div data-testid="review">
      <div class="review-title">Great product</div>
      <div class="star-rating"><span data-rating="5"></span></div>
      <time datetime="2024-01-01"></time>
      <a href="https://www.g2.com/products/acme/reviews/acme-review-123">Read</a>
    </div>
  </body>
</html>
"""

def test_parse_and_normalize_minimal():
    soup = BeautifulSoup(HTML, "lxml")
    profile = parse_product_profile(soup, url="https://www.g2.com/products/acme/reviews")
    reviews = parse_reviews(soup, url="https://www.g2.com/products/acme/reviews")
    comp = parse_competitive(soup, url="https://www.g2.com/products/acme/reviews")
    pricing = parse_pricing(soup, url="https://www.g2.com/products/acme/reviews")

    record = {**profile, **comp, **pricing}
    record["initial_reviews"] = reviews["initial_reviews"]

    normalized = normalize_record(record)
    assert normalized["product_name"] == "Acme Widget"
    assert normalized["rating"] == 4.7
    assert normalized["reviews"] == 1234
    assert normalized["categories"][0]["category_name"] == "Widget Tools"
    assert normalized["pricing_plans"][0]["plan_name"] == "Starter"
    assert normalized["alternatives"][0]["competitor_name"] == "Contoso"
    assert normalized["comparisons"][0]["link"].endswith("acme-vs-contoso")
    assert normalized["initial_reviews"][0]["review_rating"] == 5.0
    for k in ["1","2","3","4","5"]:
        assert k in normalized["star_distribution"]