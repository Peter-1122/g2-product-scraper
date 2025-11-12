from typing import Dict, Any, List

CORE_FIELDS = [
    "product_id", "product_name", "product_logo", "g2_link", "what_is", "product_description",
    "positioning_against_competitor", "reviews", "rating", "company_id", "seller", "company_phone",
    "company_location", "company_founded_year", "company_annual_revenue", "company_ownership",
    "discussions_link", "supported_languages", "twitter", "number_of_followers_on_twitter",
    "linkedin", "number_of_employees_on_linkedin", "product_website", "company_website", "is_claimed",
    "categories", "screenshots", "videos", "download_links", "pricing_plans", "alternatives",
    "comparisons", "star_distribution", "g2_reviews_link", "initial_reviews"
]

def normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize field types and ensure all core fields exist.
    """
    normalized: Dict[str, Any] = {k: record.get(k) for k in CORE_FIELDS}

    # Coerce types
    if normalized.get("reviews") is not None:
        try:
            normalized["reviews"] = int(normalized["reviews"])
        except Exception:
            normalized["reviews"] = None

    if normalized.get("rating") is not None:
        try:
            normalized["rating"] = float(normalized["rating"])
        except Exception:
            normalized["rating"] = None

    # Ensure arrays are arrays
    for key in ["categories", "screenshots", "videos", "download_links", "pricing_plans", "alternatives", "comparisons", "initial_reviews"]:
        if normalized.get(key) is None:
            normalized[key] = []
        elif not isinstance(normalized[key], list):
            normalized[key] = [normalized[key]]

    # Star distribution ensure keys "1".."5"
    sd = normalized.get("star_distribution") or {}
    out_sd = {}
    for i in range(1, 6):
        try:
            out_sd[str(i)] = int(sd.get(str(i), 0))
        except Exception:
            out_sd[str(i)] = 0
    normalized["star_distribution"] = out_sd

    # Categories cleanup
    normalized["categories"] = [
        {"category_name": c.get("category_name"), "category_link": c.get("category_link")}
        for c in normalized["categories"]
        if isinstance(c, dict)
    ]

    return normalized