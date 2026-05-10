from __future__ import annotations
from dotenv import load_dotenv
load_dotenv()

from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
from typing import Any, Dict, List

import streamlit as st

from ai_parser import Preferences, parse_preferences
from ai_ranker import rank_restaurants_with_ai


MOCK_RESTAURANTS: List[Dict[str, Any]] = [
 {
 "id": "r1",
 "name": "The Quiet Table",
 "cuisine": "continental",
 "vibe": "quiet upscale",
 "distance_km": 3.2,
 "rating": 4.7,
 "budget": "mid",
 "capacity": 4,
 "eta_min": 12,
 "features": ["candles", "anniversary", "private corner", "vegetarian-friendly"],
 },
 {
 "id": "r2",
 "name": "Spice Harbor",
 "cuisine": "asian",
 "vibe": "lively modern",
 "distance_km": 5.8,
 "rating": 4.5,
 "budget": "mid",
 "capacity": 6,
 "eta_min": 18,
 "features": ["shareable plates", "bar seating", "late-night", "reservations"],
 },
 {
 "id": "r3",
 "name": "Luna Bistro",
 "cuisine": "continental",
 "vibe": "chill cozy",
 "distance_km": 8.5,
 "rating": 4.8,
 "budget": "high",
 "capacity": 2,
 "eta_min": 25,
 "features": ["romantic", "quiet", "dessert menu", "birthday plate"],
 },
 {
 "id": "r4",
 "name": "Street Bowl",
 "cuisine": "casual fusion",
 "vibe": "casual fast",
 "distance_km": 2.0,
 "rating": 4.2,
 "budget": "low",
 "capacity": 8,
 "eta_min": 8,
 "features": ["quick service", "group friendly", "takeaway", "no-reservation"],
 },
 {
 "id": "r5",
 "name": "Amber Room",
 "cuisine": "continental",
 "vibe": "quiet premium",
 "distance_km": 6.1,
 "rating": 4.6,
 "budget": "high",
 "capacity": 4,
 "eta_min": 16,
 "features": ["soft lighting", "birthday dessert", "date night", "wine list"],
 },
]


def search_restaurants(prefs: Preferences) -> List[Dict[str, Any]]:
 results = []
 for r in MOCK_RESTAURANTS:
  if prefs.distance_km and float(r["distance_km"]) > float(prefs.distance_km):
   continue
  if prefs.rating_min and float(r["rating"]) < float(prefs.rating_min):
   continue
  if prefs.cuisine_style != "any" and prefs.cuisine_style.lower() not in str(r["cuisine"]).lower():
   continue
  if prefs.budget != "any" and prefs.budget.lower() != str(r["budget"]).lower():
   continue
 results.append(r)

 if not results:
  for r in MOCK_RESTAURANTS:
   if prefs.rating_min and float(r["rating"]) < float(prefs.rating_min):
    continue
   if prefs.cuisine_style != "any" and prefs.cuisine_style.lower() not in str(r["cuisine"]).lower():
    continue
 results.append(r)

 return results


def book_restaurant(restaurant: Dict[str, Any], prefs: Preferences) -> Dict[str, Any]:
 return {
 "booking_id": f"BK-{restaurant['id'].upper()}-{prefs.party_size}",
 "restaurant": restaurant["name"],
 "party_size": prefs.party_size,
 "status": "confirmed",
 }


st.set_page_config(page_title="AI Restaurant Assistant", page_icon="🍽️", layout="wide")
st.title("AI Restaurant Assistant")
st.write("Type a messy request like: “Somewhere chill, not too far, good for a birthday dinner for 2.”")

user_text = st.text_area(
 "Describe what you want",
 height=120,
 placeholder="Somewhere quiet, slightly upscale, not too far, birthday dinner for 2",
)

col1, col2 = st.columns(2)
with col1:
 run_button = st.button("Find restaurants", type="primary")
with col2:
 st.caption("Tip: try adding vibe, distance, occasion, or budget.")

if run_button and user_text.strip():
 with st.spinner("Parsing your intent..."):
  prefs = parse_preferences(user_text)

 st.subheader("Parsed preferences")
 st.json(prefs.__dict__)

 shortlist = search_restaurants(prefs)

 st.subheader("Shortlist from tools")
 st.write(f"{len(shortlist)} restaurants matched the current filters.")
 for r in shortlist:
  st.write(f"- {r['name']} | {r['cuisine']} | {r['vibe']} | {r['distance_km']} km | rating {r['rating']}")

 with st.spinner("Ranking the shortlist..."):
  ranked_payload = rank_restaurants_with_ai(prefs, shortlist)

 ranked = ranked_payload["ranked"]
 top_reason = ranked_payload["top_reason"]
 tradeoffs = ranked_payload["tradeoffs"]

 st.subheader("Best recommendation")
 if ranked:
  top = ranked[0]
  st.markdown(f"### {top['name']}")
  st.write(top_reason)
  st.write(tradeoffs)
  st.write(
   f"Distance: {top['distance_km']} km | Rating: {top['rating']} | Vibe: {top['vibe']} | ETA: {top['eta_min']} min"
  )

  if st.button("Book this one"):
   booking = book_restaurant(top, prefs)
   st.success(
    f"Booked {booking['restaurant']} for {booking['party_size']} people. Booking ID: {booking['booking_id']}"
   )

 st.subheader("Ranked list")
 for i, r in enumerate(ranked[:5], start=1):
  score = r.get("score", "AI ranked")
  st.write(f"{i}. {r['name']} — {score}")

elif run_button:
 st.warning("Please enter a request first.")