from typing import Dict, Any, List
from bs4 import BeautifulSoup

def parse_competitive(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """
    Extract alternatives and comparison links.
    """
    alternatives: List[Dict[str, Any]] = []
    comparisons: List[Dict[str, Any]] = []

    # Alternatives list guess
    for row in soup.select("a[href*='/products/'][href*='/reviews']"):
        name = row.get_text(strip=True)
        href = row.get("href")
        if name and href and "g2.com/products/" in href:
            if not any(a["competitor_link"] == href for a in alternatives):
                alternatives.append({
                    "competitor_name": name,
                    "competitor_link": href,
                    "competitor_rating": None,
                    "competitor_reviews": None,
                })

    # Comparisons like /compare/x-vs-y
    for a in soup.select("a[href*='/compare/']"):
        href = a.get("href")
        label = a.get_text(strip=True)
        if href:
            comparisons.append({
                "link": href,
                "competitor_name": label or None
            })

    return {"alternatives": alternatives, "comparisons": comparisons}