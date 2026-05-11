"""
simulate_saas_reviews.py
========================
Generates realistic synthetic SaaS product review data and performs
rule-based "AI" analysis (sentiment, pain-points, feature requests, topics,
business-priority scoring, and executive-level summaries).

This module is the single source of truth for all generated data.
It is called by backend/load_saas_db.py to populate the MySQL database.

Why simulated data?
- Keeps the project stable and portfolio-friendly (no external API keys).
- Demonstrates analytical thinking, not just scraping skills.
- Allows deterministic, repeatable datasets for demo purposes.
"""

import random
import json
from datetime import datetime, timedelta

# ────────────────────────────────────────────────────────────────
# PRODUCT CATALOG — 8 realistic SaaS products with personality
# Each product has inherent strengths/weaknesses that bias reviews.
# ────────────────────────────────────────────────────────────────
SAAS_PRODUCTS = [
    {"name": "FlowDesk CRM",        "category": "CRM & Sales",
     "strength": "pipeline visibility", "weakness": "customization",
     "rating_bias": 0.1},
    {"name": "TaskPilot",            "category": "Project Management",
     "strength": "workflow features",   "weakness": "onboarding complexity",
     "rating_bias": 0.0},
    {"name": "CloudSecure",          "category": "Cybersecurity",
     "strength": "reliability",         "weakness": "pricing",
     "rating_bias": -0.1},
    {"name": "InsightBoard",         "category": "Data Analytics",
     "strength": "analytics depth",     "weakness": "integrations",
     "rating_bias": 0.15},
    {"name": "TeamSync",             "category": "Team Collaboration",
     "strength": "collaboration ease",  "weakness": "reporting",
     "rating_bias": 0.05},
    {"name": "SupportHub",           "category": "Customer Support",
     "strength": "support workflows",   "weakness": "performance",
     "rating_bias": -0.05},
    {"name": "AutomatePro",          "category": "Workflow Automation",
     "strength": "automation power",    "weakness": "setup complexity",
     "rating_bias": 0.0},
    {"name": "DataFlow Analytics",   "category": "Business Intelligence",
     "strength": "dashboards",          "weakness": "difficult setup",
     "rating_bias": 0.1},
]

# ────────────────────────────────────────────────────────────────
# REALISTIC REVIEW TEMPLATES — sound like actual SaaS feedback
# ────────────────────────────────────────────────────────────────

POSITIVE_REVIEWS = [
    "The dashboard builder is intuitive, and our team was able to create reporting workflows without needing engineering support.",
    "We onboarded our entire sales team in under a week. The guided setup wizard made adoption effortless.",
    "The automation rules saved our operations team roughly 12 hours per week on repetitive tasks.",
    "I'm impressed with the real-time collaboration features. Our remote team communicates much more efficiently now.",
    "The customer support team responded within minutes and resolved our billing issue on the first call.",
    "Security compliance was a major factor in our decision. SOC 2 readiness out of the box was a game-changer.",
    "The API is well-documented and our developers integrated it into our internal tools within a single sprint.",
    "Analytics dashboards are visually clean and the drill-down capabilities are surprisingly powerful for the price.",
    "Role-based permissions work exactly as expected — critical for our enterprise compliance requirements.",
    "The mobile app works well for on-the-go approvals. Not many competitors offer this level of mobile functionality.",
    "Pricing is transparent and competitive compared to alternatives like Salesforce and HubSpot.",
    "The reporting module generates executive-ready summaries that I can share directly with the C-suite.",
    "AI-powered suggestions for task prioritization have noticeably improved our sprint planning accuracy.",
    "Integrations with Slack and Jira were seamless. Our team barely noticed the switch.",
    "The product roadmap is public and the team ships regularly. This gives us confidence in the long-term investment.",
    "Custom fields and workflow templates make it adaptable to our unique processes without developer involvement.",
    "Data export to CSV and Excel works reliably, which is critical for our monthly board reporting.",
    "The notification system is well-designed — configurable enough to avoid alert fatigue.",
    "Uptime has been excellent. We haven't experienced a single outage in six months of use.",
    "The onboarding team provided a dedicated success manager who helped us configure everything perfectly.",
]

NEUTRAL_REVIEWS = [
    "The tool works well for daily collaboration, but advanced reporting and export options still feel limited.",
    "It does what it promises, but the UI feels dated compared to newer competitors entering the market.",
    "Setup took longer than the advertised '15-minute onboarding,' but once configured, it works reliably.",
    "Good product overall, though the pricing jumps significantly between the team and enterprise tiers.",
    "The core features are solid, but we've hit several limitations when trying to customize workflows.",
    "Customer support is responsive during business hours, but there's no weekend or after-hours coverage.",
    "The desktop experience is great, but the mobile app is noticeably behind in feature parity.",
    "Works fine for small teams, but we're starting to see performance degradation as our dataset grows.",
    "The integrations work, but they feel like add-ons rather than native parts of the product experience.",
    "It meets our basic needs, but we're evaluating competitors that offer more advanced automation features.",
    "The dashboard is useful but lacks the customization depth we need for stakeholder-specific views.",
    "Onboarding documentation exists but it's somewhat outdated and doesn't cover the newer feature set.",
    "The product is stable but innovation seems to have slowed — the last major feature was released months ago.",
    "Adequate for our current scale, but I have concerns about whether it will handle our growth trajectory.",
    "The reporting tools are functional but don't match the visualization quality of dedicated BI platforms.",
]

NEGATIVE_REVIEWS = [
    "Initial onboarding took longer than expected, and the permission settings were confusing for non-technical users.",
    "We've experienced three significant outages in the past quarter. For a security product, this is unacceptable.",
    "The pricing model changed without adequate notice, and our monthly costs increased by nearly 40%.",
    "Integration with our existing Salesforce instance was problematic and required extensive custom development.",
    "The search functionality is painfully slow with large datasets. Finding specific records takes far too long.",
    "Customer support tickets regularly take 48+ hours for initial response, which is far below industry standards.",
    "The mobile app crashes frequently on both iOS and Android. Our field team has essentially stopped using it.",
    "Reporting customization is extremely limited — we can't even change date ranges on standard reports.",
    "The API documentation is incomplete and several endpoints behave differently than described.",
    "Workflow automation has a steep learning curve and the error messages are not helpful for debugging.",
    "Export functionality only supports CSV, with no option for PDF or formatted Excel output.",
    "Permission management requires admin-level access for simple changes, creating bottlenecks.",
    "The notification system is overwhelming — we receive 50+ alerts daily with no effective filtering options.",
    "Data migration from our previous tool was a nightmare. No import wizard or mapping tools are available.",
    "The product lacks basic audit logging, which is a compliance blocker for our regulated industry.",
    "Admin controls are insufficient for enterprise use. We can't enforce password policies or session timeouts.",
    "The AI features feel gimmicky and don't provide actionable insights for our business context.",
    "Performance degrades significantly during peak hours (9-11am), affecting our entire team's productivity.",
    "The dashboard loading time averages 8+ seconds, which is frustrating for daily operational use.",
    "Multi-language support is minimal, limiting adoption across our international offices.",
]

# Feature request templates (mapped from pain areas)
FEATURE_REQUESTS = [
    "Better mobile app experience",
    "AI-powered summarization and insights",
    "Customizable reporting templates",
    "SSO and SAML authentication",
    "Improved API documentation",
    "Guided onboarding wizard",
    "Dark mode interface option",
    "Bulk data export (CSV, PDF, Excel)",
    "Real-time collaboration features",
    "Slack and Microsoft Teams integration",
    "Role-based access control (RBAC)",
    "Workflow automation builder",
    "Performance optimization for large datasets",
    "Advanced search and filtering",
    "Multi-language support",
    "Audit logging and compliance tools",
]

# Reviewer roles — weighted by frequency in real B2B SaaS reviews
ROLES = [
    ("Product Manager",          15),
    ("Software Engineer",        12),
    ("Marketing Manager",         8),
    ("CEO / Founder",             5),
    ("Data Analyst",             12),
    ("CTO",                       4),
    ("Operations Manager",       10),
    ("Customer Success Manager",  8),
    ("IT Administrator",         10),
    ("Business Analyst",          8),
    ("Support Team Lead",         5),
    ("Sales Director",            3),
]
ROLE_NAMES   = [r[0] for r in ROLES]
ROLE_WEIGHTS = [r[1] for r in ROLES]


# ────────────────────────────────────────────────────────────────
# REVIEW GENERATOR
# ────────────────────────────────────────────────────────────────
def generate_review(product_id, product):
    """
    Generates one synthetic review for a given product.
    The product's inherent bias affects rating distribution.
    """
    product_name = product["name"]

    # Base rating weights (skewed positive like real review platforms)
    # then shift by product bias
    base_weights = [5, 10, 18, 32, 35]
    bias = product.get("rating_bias", 0)
    # Bias shifts probability toward higher or lower ratings
    weights = [
        max(1, base_weights[0] - bias * 10),
        max(1, base_weights[1] - bias * 8),
        max(1, base_weights[2]),
        max(1, base_weights[3] + bias * 8),
        max(1, base_weights[4] + bias * 10),
    ]
    rating = random.choices([1, 2, 3, 4, 5], weights=weights)[0]

    is_positive = rating >= 4
    is_neutral  = rating == 3

    # Select review text based on sentiment
    if is_positive:
        text = random.choice(POSITIVE_REVIEWS)
        sentiment = "Positive"
        # Occasionally weave in product-specific strength
        if random.random() < 0.3:
            text += f" {product_name}'s {product['strength']} is particularly strong."
    elif is_neutral:
        text = random.choice(NEUTRAL_REVIEWS)
        sentiment = "Neutral"
    else:
        text = random.choice(NEGATIVE_REVIEWS)
        sentiment = "Negative"
        # Occasionally weave in product-specific weakness
        if random.random() < 0.4:
            text += f" The {product['weakness']} issue with {product_name} needs urgent attention."

    # Extract realistic pros and cons from the review text
    pros = []
    cons = []
    pro_signals  = ["intuitive", "seamless", "excellent", "impressed", "powerful",
                    "saved", "reliable", "clean", "competitive", "effortless",
                    "responsive", "well-documented", "configurable"]
    con_signals  = ["slow", "confusing", "expensive", "crash", "limited",
                    "outdated", "painful", "frustrating", "unacceptable",
                    "overwhelming", "degradation", "nightmare"]

    text_lower = text.lower()
    for sig in pro_signals:
        if sig in text_lower:
            pros.append(sig + " experience")
    for sig in con_signals:
        if sig in text_lower:
            cons.append(sig + " issues")

    if not pros and is_positive:
        pros = ["solid product overall"]
    if not cons and not is_positive and not is_neutral:
        cons = ["needs improvement"]

    # Review date — spread across last 12 months with realistic distribution
    # More reviews in recent months (recency bias)
    months_ago = random.choices(range(12), weights=[20, 17, 14, 12, 10, 8, 6, 5, 4, 3, 2, 1])[0]
    day_offset = random.randint(0, 28)
    review_date = (datetime.now() - timedelta(days=months_ago * 30 + day_offset)).date()

    return {
        "product_id":      product_id,
        "review_text":     text,
        "rating":          rating,
        "reviewer_role":   random.choices(ROLE_NAMES, weights=ROLE_WEIGHTS)[0],
        "review_date":     review_date.isoformat(),
        "pros":            json.dumps(pros[:3]),
        "cons":            json.dumps(cons[:3]),
        "source_url":      f"https://g2.com/products/{product_name.lower().replace(' ', '-')}/reviews/{random.randint(100000, 999999)}",
        # Temporary keys for the analysis function
        "mock_sentiment":    sentiment,
        "mock_pain_points":  cons,
        "mock_features":     pros,
    }


# ────────────────────────────────────────────────────────────────
# SIMULATED AI ANALYSIS
# ────────────────────────────────────────────────────────────────
def analyze_review_simulated(review):
    """
    Rule-based 'AI' analysis of a single review.
    In production this could be replaced with an LLM call or NLP model.
    Returns a dict matching the review_analysis table schema.
    """
    sentiment    = review["mock_sentiment"]
    pain_points  = review["mock_pain_points"]

    # ── Feature Request Extraction ──
    feature_requests = []
    text_lower = review["review_text"].lower()

    pain_to_feature = {
        "mobile":        "Better mobile app experience",
        "report":        "Customizable reporting templates",
        "export":        "Bulk data export (CSV, PDF, Excel)",
        "integrat":      "Slack and Microsoft Teams integration",
        "onboarding":    "Guided onboarding wizard",
        "permission":    "Role-based access control (RBAC)",
        "api":           "Improved API documentation",
        "automation":    "Workflow automation builder",
        "search":        "Advanced search and filtering",
        "performance":   "Performance optimization for large datasets",
        "ai":            "AI-powered summarization and insights",
        "sso":           "SSO and SAML authentication",
        "language":      "Multi-language support",
        "audit":         "Audit logging and compliance tools",
        "dark mode":     "Dark mode interface option",
    }
    for keyword, feature in pain_to_feature.items():
        if keyword in text_lower:
            feature_requests.append(feature)

    # Sometimes add a generic request even for positive reviews
    if not feature_requests and random.random() < 0.2:
        feature_requests.append(random.choice(FEATURE_REQUESTS))

    # ── Topic Classification ──
    if any(kw in text_lower for kw in ["expensive", "pricing", "cost", "price", "billing", "tier"]):
        topic = "Pricing"
    elif any(kw in text_lower for kw in ["support", "help desk", "ticket", "response time"]):
        topic = "Customer Support"
    elif any(kw in text_lower for kw in ["crash", "outage", "downtime", "uptime", "stable"]):
        topic = "Reliability"
    elif any(kw in text_lower for kw in ["ui", "intuitive", "confusing", "interface", "design", "mobile app"]):
        topic = "UX / UI"
    elif any(kw in text_lower for kw in ["integration", "api", "salesforce", "slack", "jira", "sso"]):
        topic = "Integrations"
    elif any(kw in text_lower for kw in ["onboarding", "setup", "learning curve", "documentation", "migration"]):
        topic = "Onboarding"
    elif any(kw in text_lower for kw in ["automation", "ai", "workflow", "summarization"]):
        topic = "AI & Automation"
    elif any(kw in text_lower for kw in ["report", "analytics", "dashboard", "export", "csv", "excel"]):
        topic = "Reporting"
    elif any(kw in text_lower for kw in ["security", "compliance", "permission", "audit", "rbac", "password"]):
        topic = "Security"
    elif any(kw in text_lower for kw in ["performance", "slow", "loading", "speed", "degradat"]):
        topic = "Performance"
    else:
        topic = "General"

    # ── Business Priority Score (0-10) ──
    priority = (6 - review["rating"]) * 1.5
    if review["reviewer_role"] in ["CEO / Founder", "CTO", "Sales Director"]:
        priority += 2.5
    elif review["reviewer_role"] in ["Product Manager", "Business Analyst", "Operations Manager"]:
        priority += 1.5
    if len(pain_points) >= 2:
        priority += 1.0
    if sentiment == "Negative":
        priority += 0.5
    priority = round(min(max(priority, 0.5), 10.0), 1)

    # ── Short Business Summary ──
    role = review["reviewer_role"]
    r    = review["rating"]
    parts = [f"{role} rated {r}/5."]
    if sentiment == "Negative":
        parts.append(f"Key concern: {topic}.")
    elif sentiment == "Positive":
        parts.append(f"Praised: {topic}.")
    else:
        parts.append(f"Mixed feedback on {topic}.")
    if feature_requests:
        parts.append(f"Requests: {feature_requests[0]}.")
    summary = " ".join(parts)

    return {
        "sentiment":                sentiment,
        "pain_points":              json.dumps(pain_points),
        "feature_requests":         json.dumps(feature_requests),
        "topic_classification":     topic,
        "business_priority_score":  priority,
        "short_business_summary":   summary,
    }


# ────────────────────────────────────────────────────────────────
# DATASET GENERATOR — called by load_saas_db.py
# ────────────────────────────────────────────────────────────────
def generate_dataset(num_reviews=300):
    """
    Generates the full dataset: products list, reviews list, analyses list.
    product_id values in reviews are 1-indexed to match MySQL AUTO_INCREMENT.
    """
    products = SAAS_PRODUCTS
    reviews  = []
    analyses = []

    for _ in range(num_reviews):
        product_idx = random.randint(0, len(products) - 1)
        product     = products[product_idx]
        product_id  = product_idx + 1

        review   = generate_review(product_id, product)
        analysis = analyze_review_simulated(review)

        reviews.append(review)
        analyses.append(analysis)

    return products, reviews, analyses


# Quick sanity check when run directly
if __name__ == "__main__":
    products, reviews, analyses = generate_dataset(5)
    print(f"Generated {len(products)} products, {len(reviews)} reviews, {len(analyses)} analyses.")
    for i in range(min(3, len(reviews))):
        print(f"\n--- Review {i+1} ---")
        print(f"  Text:      {reviews[i]['review_text'][:120]}...")
        print(f"  Sentiment: {analyses[i]['sentiment']}")
        print(f"  Topic:     {analyses[i]['topic_classification']}")
        print(f"  Priority:  {analyses[i]['business_priority_score']}")
