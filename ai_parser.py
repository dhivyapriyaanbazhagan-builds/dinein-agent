# ai_parser.py
from __future__ import annotations
from dotenv import load_dotenv
load_dotenv()

from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List

from google import genai


@dataclass
class Preferences:
 cuisine_style: str = "any"
 vibe: str = "any"
 occasion: str = "any"
 distance_km: int = 10
 party_size: int = 2
 budget: str = "any"
 rating_min: float = 4.0
 must_haves: List[str] = field(default_factory=list)
 avoid: List[str] = field(default_factory=list)
 notes: str = ""


client = genai.Client()


def _extract_json(text: str) -> Dict[str, Any]:
 text = (text or "").strip()

 try:
  return json.loads(text)
 except json.JSONDecodeError:
  pass

 start = text.find("{")
 end = text.rfind("}")
 if start == -1 or end == -1 or end <= start:
  raise ValueError(f"No JSON object found in model output: {text[:200]}")

 return json.loads(text[start : end + 1])


def _coerce_preferences(raw: Dict[str, Any]) -> Preferences:
 def _int(value: Any, default: int) -> int:
  try:
   return int(value)
  except Exception:
   return default

 def _float(value: Any, default: float) -> float:
  try:
   return float(value)
  except Exception:
   return default

 def _list(value: Any) -> List[str]:
  if isinstance(value, list):
   return [str(x).strip() for x in value if str(x).strip()]
  return []

 return Preferences(
 cuisine_style=str(raw.get("cuisine_style", "any")).strip() or "any",
 vibe=str(raw.get("vibe", "any")).strip() or "any",
 occasion=str(raw.get("occasion", "any")).strip() or "any",
 distance_km=_int(raw.get("distance_km", 10), 10),
 party_size=_int(raw.get("party_size", 2), 2),
 budget=str(raw.get("budget", "any")).strip() or "any",
 rating_min=_float(raw.get("rating_min", 4.0), 4.0),
 must_haves=_list(raw.get("must_haves", [])),
 avoid=_list(raw.get("avoid", [])),
 notes=str(raw.get("notes", "")).strip(),
 )


def parse_preferences(user_text: str, model: str | None = None) -> Preferences:
 """
 Turns messy free text into structured restaurant preferences.
 """
 model_name = model or os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

 prompt = f"""
You are a restaurant intent parser.

Turn the user's text into ONE JSON object with exactly these keys:
- cuisine_style: string
- vibe: string
- occasion: string
- distance_km: integer
- party_size: integer
- budget: string
- rating_min: number
- must_haves: array of strings
- avoid: array of strings
- notes: string

Rules:
- Use "any" when the user does not specify a field.
- Infer reasonable defaults, but do not invent strong preferences.
- Keep arrays short and practical.
- Return JSON only. No markdown. No explanation.

User text:
{user_text}
""".strip()

 response = client.models.generate_content(
 model=model_name,
 contents=prompt,
 )

 raw_text = getattr(response, "text", "") or ""
 raw = _extract_json(raw_text)
 return _coerce_preferences(raw)


def preferences_to_dict(prefs: Preferences) -> Dict[str, Any]:
 return asdict(prefs)