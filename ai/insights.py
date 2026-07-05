from collections import defaultdict
from datetime import datetime
from database.crud import get_detailed_receipts
from config import GROQ_API_KEY
import json
import requests

def build_analytics_from_receipts(receipts):

    total_spent = 0
    category_summary = defaultdict(float)
    vendor_summary = defaultdict(lambda: {"total_spent": 0.0, "visit_count": 0})
    monthly_summary = defaultdict(float)

    highest_transaction = 0
    lowest_transaction = float("inf")
    transaction_count = 0

    for r in receipts:
        amount = float(r.get("total_amount", 0))
        category = r.get("purchase_category", "unknown")
        vendor = r.get("supplier_name", "unknown")
        date_str = r.get("date")

        total_spent += amount
        transaction_count += 1

        category_summary[category] += amount
        vendor_summary[vendor]["total_spent"] += amount
        vendor_summary[vendor]["visit_count"] += 1

        if amount > highest_transaction:
            highest_transaction = amount
        if amount < lowest_transaction:
            lowest_transaction = amount

        # monthly grouping (safe parse)
        if date_str:
            try:
                month = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m")
                monthly_summary[month] += amount
            except:
                pass

    avg_transaction = total_spent / transaction_count if transaction_count else 0

    # round category + monthly values
    categories = {k: round(v, 2) for k, v in category_summary.items()}
    monthly_summary = {k: round(v, 2) for k, v in sorted(monthly_summary.items())}

    # round vendor totals
    for v in vendor_summary.values():
        v["total_spent"] = round(v["total_spent"], 2)

    top_vendors = sorted(
        vendor_summary.items(),
        key=lambda x: x[1]["total_spent"],
        reverse=True
    )[:5]
    top_vendors = [{"name": name, **data} for name, data in top_vendors]

    category_percentages = {
        k: round((v / total_spent) * 100, 2)
        for k, v in categories.items()
    } if total_spent else {}

    return {
        "summary": {
            "total_spent": round(total_spent, 2),
            "transaction_count": transaction_count,
            "avg_transaction": round(avg_transaction, 2)
        },

        "categories": categories,
        "category_percentages": category_percentages,

        "vendors": {k: v for k, v in vendor_summary.items()},
        "top_vendors": top_vendors,

        "monthly_summary": monthly_summary,

        "extremes": {
            "highest_transaction": round(highest_transaction, 2),
            "lowest_transaction": round(lowest_transaction, 2) if lowest_transaction != float("inf") else 0
        }
    }


def ai_analytics_data():
    receipts = get_detailed_receipts()
    return build_analytics_from_receipts(receipts)

def get_ai_insights(analytics_data):
    prompt = f"""
You are a personal finance assistant. Analyze this expense data and return ONLY a JSON object, no explanation, no markdown, no extra text.

Data:
{json.dumps(analytics_data, indent=2)}

Return exactly this structure:
{{
  "summary_line": "One sentence overview using actual numbers e.g. You spent ₹5500 this period, mostly on shopping.",

  "spending_personality": "A fun label like The Foodie, The Shopaholic, The Traveller, The Tech Buyer etc — based on their top category",

  "insights": [
    "Specific observation using actual numbers from the data",
    "Another specific observation",
    "Another specific observation",
    "Another specific observation"
  ],

  "warnings": [
    "Something concerning e.g. one vendor taking over 50% of total budget",
    "Another warning if applicable, else omit this item"
  ],

  "tip_of_the_day": "One specific actionable tip based on their actual spending pattern",

  "detailed_advice": {{
    "category_name_1": "Specific advice for their top spending category",
    "category_name_2": "Specific advice for second category if exists"
  }},

  "monthly_forecast": "Based on current pace, you will spend approximately ₹X this month — one sentence",

  "score": {{
    "value": 75,
    "label": "Good",
    "reason": "One line explaining why they got this score"
  }}
}}

Rules:
- Use ACTUAL numbers from the data, never make up numbers
- Be specific and personal, not generic
- insights and warnings must be under 20 words each
- score value must be between 0 and 100
- label must be one of: Poor, Average, Good, Excellent
- detailed_advice keys must be actual category names from their data
- Return ONLY the JSON, absolutely nothing else
"""

    response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.4
            },
            timeout=60
        )
    
    response.raise_for_status()
    
    raw = response.json()["choices"][0]["message"]["content"].strip()
    
    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()
    
    return json.loads(raw)
