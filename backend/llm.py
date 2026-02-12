import urllib.parse
import os
import json
import requests
from bs4 import BeautifulSoup
from groq import Groq

from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
import requests
import urllib.parse
from bs4 import BeautifulSoup

def fetch_product_image(product_name):
    """
    Fetch real product images using Bing (safe + reliable + no API required).
    Works for phones, laptops, watches, headphones, etc.
    """
    try:
        query = urllib.parse.quote(product_name)
        url = f"https://www.bing.com/images/search?q={query}&form=HDRSC2"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")

        # Bing stores images in <img class=mimg>
        img = soup.find("img", class_="mimg")
        if img and img.get("src"):
            return img["src"]

        return None

    except Exception as e:
        print("Image fetch error:", e)
        return None


def fetch_price_from_web(product_name):
    """
    Use LLM to estimate the product price realistically (Indian market).
    Fully reliable and works for any product.
    """
    prompt = f"""
    Give ONLY the approximate price in INR for the product: {product_name}.
    Only return a number. Example: 25999
    """

    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )

        price_text = resp.choices[0].message.content.strip()
        price_value = int("".join(filter(str.isdigit, price_text)))

        return price_value, "INR", None
    except:
        return None, None, None


# correct code
# def call_llm_for_product(product_name, budget, category="general", compare_with=None):
#     """
#     Build a structured prompt to ask the model to return strict JSON.
#     Output JSON keys:
#       - overview, features[], pros[], cons[], budget_fit, alternative, alternatives[], 
#         scores {performance, battery, value}, bullets[], category_advice
#     """
#     # strict JSON schema in prompt to ensure parseable output
#     prompt = f"""
# You MUST respond ONLY with valid JSON and nothing else (no markdown, no commentary).
# Follow this EXACT schema:

# {{
#   "overview": "string",
#   "features": ["string","string","string"],
#   "pros": ["string","string","string"],
#   "cons": ["string","string","string"],
#   "budget_fit": "string",
#   "alternative": "string",
#   "alternatives": ["string","string","string"],
#   "scores": {{
#      "performance": "0-10",
#      "battery": "0-10",
#      "value": "0-10"
#   }},
#   "bullets": ["short bullet","short bullet","short bullet"],
#   "category_advice": "string"
# }}

# Now generate the JSON for the product: \"{product_name}\".
# User budget (INR): {budget}
# Category: {category}
# If comparing, compare briefly with: \"{compare_with}\" and include comparison in the "alternative" and "alternatives" fields.
# Keep each field short and beginner-friendly.
# Only output JSON.
# """
#     try:
#         resp = client.chat.completions.create(
#             model="llama-3.1-8b-instant",
#             temperature=0,
#             messages=[{"role": "user", "content": prompt}]
#         )
#         content = resp.choices[0].message.content.strip()
#         # remove code fences if present
#         content = content.replace("```json", "").replace("```", "").strip()
#         data = json.loads(content)
#         return data, content
#     except Exception as e:
#         # return a safe fallback with error logged content
#         print("LLM error:", e)
#         try:
#             # try to salvage by returning partial fields
#             return {
#                 "overview": f"Could not get a structured response from LLM for {product_name}.",
#                 "features": [],
#                 "pros": [],
#                 "cons": [],
#                 "budget_fit": "Unknown",
#                 "alternative": "",
#                 "alternatives": [],
#                 "scores": {"performance": "0", "battery": "0", "value": "0"},
#                 "bullets": [],
#                 "category_advice": ""
#             }, None
#         except:
#             return {}, None
def call_llm_for_product(product_name, budget, category="general", compare_with=None):
    """
    Primary LLM call to produce structured JSON for the product.
    If compare_with is provided and the comparison fields are missing/empty,
    perform a second focused LLM call that ONLY asks for comparison JSON.
    Returns (data_dict, raw_text).
    """
    compare_text = f"Compare briefly with {compare_with}." if compare_with else ""

    # keep existing category behavior (electronics vs non-electronics) if you want
    electronics_categories = ["phone", "laptop", "tablet", "watch", "headphones", "earbuds"]
    if category not in electronics_categories:
        score_instruction = (
            "For non-electronics (soap/shampoo/food/clothes/etc) set performance, battery, value to 0 "
            "unless you can justify a different numeric score. Still include 'scores' keys."
        )
    else:
        score_instruction = "For electronics fill realistic scores from 0–10."

    prompt = f"""
You MUST return only VALID JSON. No markdown, no extra text.

{{
  "overview": "string",
  "pros": ["string","string","string"],
  "cons": ["string","string","string"],
  "features": ["string","string","string"],
  "comparison": {{
    "better_in": ["string","string"],
    "weaker_in": ["string","string"],
    "summary": "string"
  }},
  "budget_fit": "string",
  "alternative": "string",
  "alternatives": ["string","string","string"],
  "scores": {{
     "performance": "0-10",
     "battery": "0-10",
     "value": "0-10"
  }},
  "bullets": ["short bullet","short bullet","short bullet"],
  "category_advice": "string"
}}

IMPORTANT: {score_instruction}
Product: {product_name}
User Budget: {budget}
Category: {category}
{compare_text}
If you are given a compare product, include a clear comparative summary and at least one item each for 'better_in' and 'weaker_in'.
Only output JSON.
"""

    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = resp.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)
    except Exception as e:
        print("LLM error (primary):", e)
        # Return a reasonable fallback structure so frontend does not break
        fallback = {
            "overview": f"Could not fetch structured details for {product_name}.",
            "pros": [], "cons": [], "features": [],
            "comparison": {"better_in": [], "weaker_in": [], "summary": ""},
            "budget_fit": "", "alternative": "", "alternatives": [],
            "scores": {"performance": "0", "battery": "0", "value": "0"},
            "bullets": [], "category_advice": ""
        }
        return fallback, None

    # If comparison is empty or summary missing AND user provided compare_with, try a focused second call
    try:
        comp = data.get("comparison", {})
        comp_summary = (comp.get("summary") or "").strip()
        comp_better = comp.get("better_in") or []
        comp_weaker = comp.get("weaker_in") or []
    except Exception:
        comp_summary = ""
        comp_better = []
        comp_weaker = []

    if compare_with and (not comp_summary or (not comp_better and not comp_weaker)):
        # Focused prompt that only asks for comparison JSON
        focused_prompt = f"""
Return ONLY this JSON object (no surrounding text):

{{
  "better_in": ["string","string"],
  "weaker_in": ["string","string"],
  "summary": "string"
}}

Now compare these two products and fill those fields:
Product A: {product_name}
Product B: {compare_with}

Give concise, factual comparison points (one-line statements). If there is no major difference, put
"Similar" in summary and at least one sensible bullet in better_in or weaker_in explaining small differences.
Only output JSON.
"""
        try:
            resp2 = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                temperature=0.0,
                messages=[{"role": "user", "content": focused_prompt}]
            )
            raw2 = resp2.choices[0].message.content.strip()
            raw2 = raw2.replace("```json", "").replace("```", "").strip()
            comp_data = json.loads(raw2)

            # replace/merge comparison into original data
            data["comparison"] = {
                "better_in": comp_data.get("better_in", []),
                "weaker_in": comp_data.get("weaker_in", []),
                "summary": comp_data.get("summary", "").strip()
            }
        except Exception as e2:
            print("LLM error (focused comparison):", e2)
            # if even the focused call fails, ensure minimal sensible defaults
            data.setdefault("comparison", {})
            data["comparison"].setdefault("summary", "No comparison summary available.")
            data["comparison"].setdefault("better_in", ["No strong advantages found."])
            data["comparison"].setdefault("weaker_in", ["No weaknesses detected."])

    # final safety: ensure keys exist and are non-empty strings/lists
    data.setdefault("overview", data.get("overview", ""))
    data.setdefault("pros", data.get("pros", []))
    data.setdefault("cons", data.get("cons", []))
    data.setdefault("features", data.get("features", []))
    data.setdefault("comparison", {
        "better_in": ["No strong advantages found."],
        "weaker_in": ["No weaknesses detected."],
        "summary": "No comparison summary available."
    })
    data.setdefault("budget_fit", data.get("budget_fit", ""))
    data.setdefault("alternative", data.get("alternative", ""))
    data.setdefault("alternatives", data.get("alternatives", []))
    data.setdefault("scores", data.get("scores", {"performance":"0","battery":"0","value":"0"}))
    data.setdefault("bullets", data.get("bullets", []))
    data.setdefault("category_advice", data.get("category_advice", ""))

    return data, raw

def get_product_explanation(product_name, budget, category="general", compare_with=None):
    # Fetch price
    price, currency, _ = fetch_price_from_web(product_name)

    # Fetch image separately
    img_url = fetch_product_image(product_name)

    # Call LLM
    structured, raw = call_llm_for_product(product_name, budget, category, compare_with)

    structured = structured or {}
    structured.setdefault("price", None)
    structured.setdefault("currency", None)
    structured.setdefault("image", None)

    if price:
        structured["price"] = price
        structured["currency"] = currency or "INR"

    if img_url:
        structured["image"] = img_url

    # Comparison Product
    if compare_with:
        cprice, ccurr, _ = fetch_price_from_web(compare_with)
        cimg = fetch_product_image(compare_with)

        structured["compare_price"] = cprice
        structured["compare_currency"] = ccurr
        structured["compare_image"] = cimg

    return structured

# correct code
# def get_product_explanation(product_name, budget):
    prompt = f"""
You MUST respond ONLY with valid JSON.
Do NOT add explanations, markdown, or text outside JSON.
Follow this JSON format EXACTLY:

{{
  "overview": "string",
  "features": ["string", "string", "string"],
  "pros": ["string", "string", "string"],
  "cons": ["string", "string", "string"],
  "budget_fit": "string",
  "alternative": "string"
}}

Now fill this JSON format for the product "{product_name}" with user budget ₹{budget}.
Keep explanations SHORT and SIMPLE.
Only output JSON. 
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content.strip()

    # Remove unwanted codeblock markers if model includes ```json
    content = content.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(content)
    except Exception as e:
        print("JSON Error:", e)
        print("Model Output:", content)
        return {
            "overview": "JSON Parsing Failed",
            "features": [],
            "pros": [],
            "cons": [],
            "budget_fit": "No data",
            "alternative": "No alternative available"
        }

    prompt = f"""
    Explain the product "{product_name}" clearly and format your response EXACTLY in this JSON style:

    {{
      "overview": "",
      "features": ["","",""],
      "pros": ["","",""],
      "cons": ["","",""],
      "budget_fit": "",
      "alternative": ""
    }}

    User budget: ₹{budget}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except:
        return {
            "overview": "AI returned an invalid format.",
            "features": [],
            "pros": [],
            "cons": [],
            "budget_fit": "No data",
            "alternative": "Not available"
        }