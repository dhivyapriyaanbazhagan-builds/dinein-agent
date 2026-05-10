# ai_ranker.py
from __future__ import annotations
from dotenv import load_dotenv
load_dotenv()

from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

import json
import os
from typing import Any, Dict, List

from google import genai

from ai_parser import Preferences, preferences_to_dict


client = genai.Client()


def _local_score(prefs: Preferences, restaurant: Dict[str, Any]) -> float:
 score = 0.0

 score += float(restaurant.get("rating", 0)) * 10

 distance = float(restaurant.get("distance_km", 999))
 score += max(0, 20 - distance * 2)

 vibe = str(restaurant.get("vibe", "")).lower()
 cuisine = str(restaurant.get("cuisine", "")).lower()
 budget = str(restaurant.get("budget", "")).lower()

 if prefs.vibe != "any" and prefs.vibe.lower() in vibe:
  score += 15
 if prefs.cuisine_style != "any" and prefs.cuisine_style.lower() in cuisine:
  score += 15
 if prefs.budget != "any" and prefs.budget.lower() == budget:
  score += 8

 capacity = int(restaurant.get("capacity", 0))
 if capacity >= prefs.party_size:
  score += 5
 else:
  score -= 10

 features = " ".join(restaurant.get("features", [])).lower()
 for item in prefs.must_haves:
  if item.lower() in features:
   score += 4
 for item in prefs.avoid:
  if item.lower() in features:
   score -= 4

 return score


def rank_restaurants_locally(
 prefs: Preferences, restaurants: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
 scored = []
 for r in restaurants:
  item = dict(r)
  item["score"] = round(_local_score(prefs, r), 2)
  scored.append(item)
 return sorted(scored, key=lambda x: x["score"], reverse=True)


def rank_restaurants_with_ai(
 prefs: Preferences,
 restaurants: List[Dict[str, Any]],
 model: str | None = None,
) -> Dict[str, Any]:
 if not restaurants:
  return {"ranked": [], "top_reason": "No restaurants matched the filters.", "tradeoffs": ""}

 model_name = model or os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

 payload = {
 "preferences": preferences_to_dict(prefs),
 "restaurants": restaurants,
 }

 prompt = f"""
You are ranking restaurants for a user.

Return ONE JSON object with:
- ranked_ids: array of restaurant ids in best-to-worst order
- top_reason: string
- tradeoffs: string

Rules:
- Rank by the user's preferences, not just rating.
- Prefer the restaurant that best balances vibe, distance, rating, and fit.
- Use only ids that appear in the input.
- Return JSON only. No markdown. No explanation.

Input:
{json.dumps(payload, ensure_ascii=False)}
""".strip()

 try:
  response = client.models.generate_content(
   model=model_name,
   contents=prompt,
  )
  raw_text = getattr(response, "text", "") or ""

  start = raw_text.find("{")
  end = raw_text.rfind("}")
  if start == -1 or end == -1 or end <= start:
   raise ValueError("Model did not return JSON.")

  data = json.loads(raw_text[start : end + 1])
  ranked_ids = [str(x) for x in data.get("ranked_ids", [])]
  top_reason = str(data.get("top_reason", "")).strip()
  tradeoffs = str(data.get("tradeoffs", "")).strip()

  by_id = {str(r["id"]): r for r in restaurants}
  ranked = [by_id[rid] for rid in ranked_ids if rid in by_id]

  ranked_set = set(ranked_ids)
  missing = [
   r for r in rank_restaurants_locally(prefs, restaurants)
   if str(r["id"]) not in ranked_set
  ]
  ranked.extend(missing)

  return {
   "ranked": ranked,
   "top_reason": top_reason or "This option best matches the user's preferences.",
   "tradeoffs": tradeoffs or "It is the best overall fit, though some alternatives may be closer or cheaper.",
  }

 except Exception:
  ranked = rank_restaurants_locally(prefs, restaurants)
  return {
   "ranked": ranked,
   "top_reason": "AI ranking failed, so the app used the local scoring fallback.",
   "tradeoffs": "Fallback ranking is based on rating, distance, vibe, cuisine fit, and capacity.",
  }