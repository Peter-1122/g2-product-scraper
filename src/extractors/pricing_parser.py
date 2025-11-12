from typing import Dict, Any, List
from bs4 import BeautifulSoup

def parse_pricing(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """
    Extract pricing plan cards: plan name, description, and feature bullets.
    """
    plans: List[Dict[str, Any]] = []
    sections = soup.select("[data-testid='pricing'] .plan, .pricing .plan, section#pricing .plan")
    if not sections:
        # Fallback: cards with title/bullets
        sections = soup.select("section#pricing, [data-section='pricing'], .pricing")

    for sec in sections:
        name_node = sec.select_one(".plan-name, h3, h4")
        desc_node = sec.select_one(".plan-description, p")
        feature_nodes = sec.select(".plan-features li, ul li")
        plan = {
            "plan_name": name_node.get_text(strip=True) if name_node else None,
            "plan_description": desc_node.get_text(strip=True) if desc_node else None,
            "plan_features": [li.get_text(strip=True) for li in feature_nodes][:25] if feature_nodes else [],
        }
        if any(v for v in plan.values()):
            plans.append(plan)

    return {"pricing_plans": plans}