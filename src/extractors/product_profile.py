from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

def _text_or_none(node) -> Optional[str]:
    if not node:
        return None
    text = node.get_text(strip=True)
    return text or None

def parse_product_profile(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """
    Extract core product profile fields from a G2-like product page.
    This parser is resilient: it uses multiple CSS strategies to find data.
    """
    # Product name
    name = None
    for selector in [
        "h1[data-testid='product-profile-header']",
        "h1[itemprop='name']",
        "h1",
        ".product-header h1",
    ]:
        node = soup.select_one(selector)
        name = _text_or_none(node)
        if name:
            break

    # Description / what-is
    what_is = None
    for selector in [
        "[data-testid='what-is'] p",
        "section#about div p",
        "div[itemprop='description'] p",
        "div[itemprop='description']",
    ]:
        node = soup.select_one(selector)
        what_is = _text_or_none(node)
        if what_is:
            break

    # Rating and total reviews
    rating = None
    total_reviews = None
    rating_node = soup.select_one("[data-testid='average-rating'], meta[itemprop='ratingValue']")
    if rating_node:
        rating = rating_node.get("content") if rating_node.name == "meta" else _text_or_none(rating_node)
        try:
            rating = float(str(rating).strip())
        except Exception:
            rating = None

    # total reviews
    for s in [
        "[data-testid='review-count']",
        "meta[itemprop='reviewCount']",
        "a[href*='#reviews'] .count",
    ]:
        node = soup.select_one(s)
        if node:
            val = node.get("content") if node.name == "meta" else _text_or_none(node)
            try:
                total_reviews = int(str(val).replace(",", "").strip())
            except Exception:
                total_reviews = None
            break

    # Logo
    logo = None
    for s in [
        "img[itemprop='image']",
        "img[alt*='logo' i]",
        "img[src*='g2crowd']",
        "img",
    ]:
        node = soup.select_one(s)
        if node and node.get("src"):
            logo = node.get("src")
            break

    # Categories
    categories = []
    for a in soup.select("a[href*='/categories/']"):
        label = _text_or_none(a)
        href = a.get("href")
        if label and href and label.lower() not in {c["category_name"].lower() for c in categories}:
            categories.append({"category_name": label, "category_link": href})

    # Star distribution (try reading from script/meta or UI bars)
    star_distribution = {}
    # Bars like: data-star="5" data-count="123"
    for bar in soup.select("[data-star][data-count]"):
        star = bar.get("data-star")
        cnt = bar.get("data-count")
        if star and cnt:
            try:
                star_distribution[str(int(star))] = int(cnt)
            except Exception:
                pass

    # Fallback: look for 'itemprop=aggregateRating' structure
    if not star_distribution:
        for i in range(1, 6):
            # Example: <meta itemprop="ratingCount" content="123"> around star N is inconsistent on public web pages;
            # we just default to 0 when unknown.
            star_distribution[str(i)] = star_distribution.get(str(i), 0)

    # Social links and sites
    def find_link_like(keyword: str) -> Optional[str]:
        for a in soup.select("a[href]"):
            href = a.get("href", "")
            if keyword in href:
                return href
        return None

    twitter = find_link_like("twitter.com")
    linkedin = find_link_like("linkedin.com/company")
    product_site = find_link_like("features") or find_link_like("product")
    company_site = None
    for a in soup.select("a[href^='http']"):
        href = a.get("href", "")
        if "g2.com" not in href and "twitter.com" not in href and "linkedin.com" not in href:
            company_site = href
            break

    return {
        "product_id": None,
        "product_name": name,
        "product_logo": logo,
        "g2_link": url,
        "what_is": what_is,
        "product_description": what_is,
        "positioning_against_competitor": None,
        "reviews": total_reviews,
        "rating": rating,
        "company_id": None,
        "seller": name,
        "company_phone": None,
        "company_location": None,
        "company_founded_year": None,
        "company_annual_revenue": None,
        "company_ownership": None,
        "discussions_link": None,
        "supported_languages": None,
        "twitter": twitter,
        "number_of_followers_on_twitter": None,
        "linkedin": linkedin,
        "number_of_employees_on_linkedin": None,
        "product_website": product_site,
        "company_website": company_site,
        "is_claimed": None,
        "categories": categories,
        "screenshots": [],
        "videos": [],
        "download_links": [],
        "pricing_plans": [],
        "alternatives": [],
        "comparisons": [],
        "star_distribution": star_distribution,
        "g2_reviews_link": f"{url}#reviews" if url else None,
    }