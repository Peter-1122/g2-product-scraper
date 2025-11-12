from typing import Dict, Any, List
from bs4 import BeautifulSoup

def parse_reviews(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """
    Extract a small sample of reviews from a G2-like page.
    We look for common structures and fall back gracefully.
    """
    reviews: List[Dict[str, Any]] = []

    # Common structure guess:
    review_blocks = soup.select("[data-testid='review']") or soup.select(".review") or []
    for i, block in enumerate(review_blocks[:25], start=1):
        title = block.select_one("[data-testid='review-title'], .review-title")
        rating = block.select_one("[data-testid='star-rating'] [data-rating], .star-rating [data-rating]")
        date = block.select_one("time[datetime], .review-date")
        link = block.select_one("a[href*='/reviews/']")
        item = {
            "review_id": None,
            "review_title": (title.get_text(strip=True) if title else None) or f"Review #{i}",
            "review_rating": float(rating.get("data-rating")) if rating and rating.get("data-rating") else None,
            "publish_date": date.get("datetime") if date and date.get("datetime") else None,
            "review_link": link.get("href") if link else url,
        }
        reviews.append(item)

    # If none found, return empty; schema allows empty sample
    return {"initial_reviews": reviews}