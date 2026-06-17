# import urllib.parse
# import os
# import json
# import queue
# import requests
# import threading
# from bs4 import BeautifulSoup
# from dotenv import load_dotenv

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# load_dotenv(os.path.join(BASE_DIR, ".env"))

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# def call_groq(prompt, timeout=8):
#     if not GROQ_API_KEY:
#         raise RuntimeError("GROQ_API_KEY is missing. Add it to backend/.env before starting the backend.")

#     response = requests.post(
#         "https://api.groq.com/openai/v1/chat/completions",
#         headers={
#             "Authorization": f"Bearer {GROQ_API_KEY}",
#             "Content-Type": "application/json",
#         },
#         json={
#             "model": "llama-3.1-8b-instant",
#             "temperature": 0,
#             "messages": [{"role": "user", "content": prompt}],
#         },
#         timeout=timeout,
#     )
#     response.raise_for_status()
#     payload = response.json()
#     return payload["choices"][0]["message"]["content"].strip()


# def call_groq_with_deadline(prompt, deadline=7):
#     result_queue = queue.Queue(maxsize=1)

#     def worker():
#         try:
#             result_queue.put(("ok", call_groq(prompt, timeout=deadline)))
#         except Exception as exc:
#             result_queue.put(("error", exc))

#     thread = threading.Thread(target=worker, daemon=True)
#     thread.start()

#     try:
#         status, value = result_queue.get(timeout=deadline)
#     except queue.Empty:
#         raise TimeoutError("Groq request timed out.")

#     if status == "error":
#         raise value

#     return value

# # ============================================
# # CATEGORY DETECTION ENGINE
# # ============================================

# CATEGORY_KEYWORDS = {
#     "phone": [
#         "iphone", "samsung galaxy", "oneplus", "vivo", "oppo", "realme", "redmi", "poco",
#         "nokia", "motorola", "sony xperia", "pixel", "mi", "honor", "zte",
#         "sharp", "blackberry", "htc", "lg phone", "5g", "foldable", "galaxy s"
#     ],
#     "laptop": [
#         "victus", "pavilion", "omen", "inspiron", "thinkpad", "ideapad", "macbook", "tuf", "rog", "aspire",
#         "precision", "alienware", "msi", "razer", "hp laptop", "dell laptop", "asus laptop", "acer laptop",
#         "lenovo laptop", "intel core", "ryzen", "processor i7", "processor i9", "gtx", "rtx", "geforce"
#     ],
#     "watch": [
#         "apple watch", "galaxy watch", "smartwatch", "noise watch", "firebolt", "boat watch",
#         "huawei watch", "wear os", "garmin", "fossil gen", "amazfit", "fitbit", "wearable"
#     ],
#     "headphones": [
#         "airpods", "earbuds", "headphones", "neckband", "buds", "sony wh", "boat rocker",
#         "sennheiser", "bose", "jbl", "beats", "skullcandy", "wireless", "noise cancel", "earphone"
#     ]
# }


# def detect_product_category(product_name):
#     """
#     Automatically detect product category based on product name keywords.
    
#     Args:
#         product_name (str): Name of the product
        
#     Returns:
#         str: Detected category (phone, laptop, watch, headphones, or general)
#     """
#     if not product_name:
#         return "general"
    
#     product_lower = product_name.lower().strip()
    
#     # Check against category keywords (order matters - check specific first)
#     for category, keywords in CATEGORY_KEYWORDS.items():
#         for keyword in keywords:
#             if keyword.lower() in product_lower:
#                 return category
    
#     return "general"


# def fetch_product_image(product_name):
#     """
#     Fetch real product images using Bing Images.
#     Works for phones, laptops, watches, headphones, etc.
#     """
#     try:
#         query = urllib.parse.quote(product_name)
#         url = f"https://www.bing.com/images/search?q={query}&form=HDRSC2"
#         headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
#         r = requests.get(url, headers=headers, timeout=2)
#         soup = BeautifulSoup(r.text, "html.parser")
#         img = soup.find("img", class_="mimg")
#         if img and img.get("src"):
#             return img["src"]
#         return None
#     except Exception as e:
#         print(f"Image fetch error for {product_name}:", e)
#         return None


# def fetch_price_from_web(product_name):
#     """
#     Use LLM to estimate product price in Indian market (INR).
#     """
#     prompt = f"Give ONLY the approximate price in INR for: {product_name}. Return only a number. Example: 25999"
#     try:
#         price_text = call_groq_with_deadline(prompt, deadline=4)
#         price_value = int("".join(filter(str.isdigit, price_text)))
#         return price_value, "INR", None
#     except Exception as e:
#         print(f"Price fetch error for {product_name}:", e)
#         return None, None, None


# def build_fallback_analysis(product_name, budget, category="general", compare_with=None):
#     category = (category or "general").lower()
#     label = product_name.strip() if product_name else "this product"
#     compare_label = compare_with.strip() if compare_with else ""

#     feature_defaults = {
#         "phone": [
#             ("Performance", "Check the processor, RAM, storage type, and long-term software support."),
#             ("Camera", "Compare daylight photos, night mode, video stability, and selfie quality before buying."),
#             ("Battery", "Look for real-world screen-on time, charging speed, and battery health support."),
#             ("Display", "Review brightness, refresh rate, resolution, and outdoor visibility."),
#             ("Build", "Check durability, service availability, warranty, and repair cost."),
#         ],
#         "laptop": [
#             ("Processor", "Match CPU class to your workload, such as study, coding, design, or gaming."),
#             ("Memory", "Prefer enough RAM for multitasking and future software updates."),
#             ("Storage", "Choose SSD storage with enough space for apps, files, and media."),
#             ("Display", "Check screen size, brightness, color quality, and refresh rate."),
#             ("Battery", "Review practical battery life, charger size, and thermal performance."),
#         ],
#         "watch": [
#             ("Health tracking", "Check heart-rate, sleep, workout, and SpO2 tracking reliability."),
#             ("Battery", "Compare typical battery life with always-on display and tracking enabled."),
#             ("Display", "Review brightness, touch response, size, and outdoor readability."),
#             ("Compatibility", "Make sure it works well with your phone and preferred apps."),
#             ("Comfort", "Check strap quality, weight, water resistance, and daily wear comfort."),
#         ],
#         "headphones": [
#             ("Sound", "Check clarity, bass balance, codec support, and distortion at high volume."),
#             ("Noise control", "Compare active noise cancellation and transparency mode performance."),
#             ("Battery", "Review battery life per charge and total backup with the case."),
#             ("Microphone", "Check call quality in noisy environments if you take frequent calls."),
#             ("Comfort", "Check fit, weight, ear pressure, and long-session comfort."),
#         ],
#         "general": [
#             ("Quality", "Check build quality, materials, warranty, and user feedback before buying."),
#             ("Use case", "Make sure the product solves your exact daily need, not just a nice-to-have feature."),
#             ("Reliability", "Look for service support, return policy, and common complaints."),
#             ("Value", "Compare the product with similarly priced alternatives before deciding."),
#             ("Longevity", "Consider durability, spare parts, updates, and resale value."),
#         ],
#     }

#     score_defaults = {
#         "phone": {"performance": 6, "camera": 6, "battery": 6, "display": 6, "charging": 6, "value": 6},
#         "laptop": {"performance": 6, "graphics": 5, "display": 6, "battery": 6, "build_quality": 6, "value": 6},
#         "watch": {"health_tracking": 6, "battery": 6, "display": 6, "accuracy": 6, "comfort": 6, "value": 6},
#         "headphones": {"sound": 6, "bass": 6, "anc": 5, "battery": 6, "comfort": 6, "value": 6},
#         "general": {"quality": 6, "durability": 6, "safety": 6, "reliability": 6, "usability": 6, "value": 6},
#     }

#     features = [
#         {"name": name, "value": value}
#         for name, value in feature_defaults.get(category, feature_defaults["general"])
#     ]

#     comparison_summary = (
#         f"Compare verified specifications, current price, warranty, and user reviews for {label} and {compare_label} before choosing."
#         if compare_label
#         else "Add a second product to compare strengths, weaknesses, and value side by side."
#     )

#     return {
#         "detected_category": category,
#         "estimated_price": None,
#         "overview": (
#             f"{label} needs a manual check because live AI details were unavailable. "
#             "Use this as a structured buying checklist and verify current price, specifications, warranty, and reviews before purchase."
#         ),
#         "features": features,
#         "pros": [
#             "Can still be evaluated using price, warranty, reviews, and specifications.",
#             "Useful if it matches your main daily requirement and fits your budget.",
#             "Worth shortlisting only after checking seller reliability and return policy.",
#         ],
#         "cons": [
#             "Live AI details were unavailable for this request.",
#             "Specifications and pricing should be verified from the seller page.",
#             "Avoid buying if reviews, warranty, or service support are unclear.",
#         ],
#         "scores": score_defaults.get(category, score_defaults["general"]),
#         "comparison": {
#             "better_in": ["Check price, warranty, main specifications, and user reviews."],
#             "weaker_in": ["No verified live comparison data is available right now."],
#             "summary": comparison_summary,
#         },
#         "best_for": "Buyers who can verify the latest specifications, price, and warranty before purchasing.",
#         "not_recommended_for": "Buyers who need a fully verified recommendation without checking seller details.",
#         "budget_fit": f"Your budget is Rs {budget}. Confirm the current selling price before deciding.",
#         "alternative": "Compare with a trusted model from the same category and price range.",
#         "alternatives": ["Check top-rated alternatives in the same budget", "Compare warranty and service support", "Review recent customer ratings"],
#         "buying_advice": "Do not buy only from this fallback summary. Verify current price, exact model, reviews, and return policy first.",
#         "final_verdict": f"{label} is not fully verified right now. Shortlist it only after checking current price, specifications, reviews, and support.",
#         "bullets": [
#             "Verify the exact model name and seller.",
#             "Compare current price against your budget.",
#             "Check warranty, return policy, and recent reviews.",
#         ],
#     }


# def is_placeholder_analysis(data):
#     if not isinstance(data, dict):
#         return True

#     text = json.dumps(data, default=str).lower()
#     blocked_phrases = [
#         "unable to fetch",
#         "unable to generate",
#         "unable to provide",
#         "best alternative product name",
#         "brief description",
#         "pro 1",
#         "con 1",
#     ]
#     if any(phrase in text for phrase in blocked_phrases):
#         return True

#     features = data.get("features") or []
#     generic_features = 0
#     for feature in features:
#         name = str(feature.get("name", "")).strip().lower() if isinstance(feature, dict) else ""
#         if name.startswith("feature "):
#             generic_features += 1

#     scores = data.get("scores") or {}
#     generic_scores = sum(1 for key in scores if str(key).lower().startswith("score"))

#     return generic_features >= 2 or generic_scores >= 2


# def call_llm_for_product(product_name, budget, category="general", compare_with=None):
#     """
#     Call LLM to generate comprehensive product analysis with category-specific features and scores.
#     Returns (data_dict, raw_text).
#     """
    
#     # Category-specific guidance
#     category_guide = {
#         "phone": "PHONE: Features must include Processor, RAM, Storage, Camera Quality, Battery Life, Display Quality. Scores: Performance, Camera, Battery, Display, Charging, Value (each 0-10)",
#         "laptop": "LAPTOP: Features must include Processor, RAM, SSD Storage, Graphics Card, Display, Battery. Scores: Performance, Graphics, Display, Battery, Build Quality, Value (each 0-10)",
#         "watch": "WATCH: Features must include Health Tracking, Heart Rate, Sleep Tracking, Battery Life, Display, Water Resistance. Scores: Health Tracking, Battery, Display, Accuracy, Comfort, Value (each 0-10)",
#         "headphones": "HEADPHONES: Features must include Sound Quality, Bass, Noise Cancellation, Battery Life, Comfort, Microphone. Scores: Sound, Bass, ANC, Battery, Comfort, Value (each 0-10)",
#         "general": "GENERAL: Features must include Quality, Durability, Safety, Design, Reliability, Brand Trust. Scores: Quality, Durability, Safety, Reliability, Usability, Value (each 0-10)"
#     }
    
#     guide = category_guide.get(category.lower(), category_guide["general"])
#     compare_text = f"Compare with {compare_with}." if compare_with else "No comparison product."
#     score_keys = {
#         "phone": ["performance", "camera", "battery", "display", "charging", "value"],
#         "laptop": ["performance", "graphics", "display", "battery", "build_quality", "value"],
#         "watch": ["health_tracking", "battery", "display", "accuracy", "comfort", "value"],
#         "headphones": ["sound", "bass", "anc", "battery", "comfort", "value"],
#         "general": ["quality", "durability", "safety", "reliability", "usability", "value"],
#     }
#     score_template = json.dumps(
#         {key: 0 for key in score_keys.get(category.lower(), score_keys["general"])},
#         indent=4
#     )

#     prompt = f"""You are an expert Product Analysis AI.

# Product: {product_name}
# Category: {category.upper()}
# Budget: Rs {budget}
# {compare_text}

# {guide}

# Return ONLY valid JSON with ALL these fields filled:

# {{
#   "detected_category": "{category}",
#   "estimated_price": 0,
#   "overview": "2-3 sentence professional summary",
#   "features": [
#     {{"name": "Feature 1", "value": "Brief description"}},
#     {{"name": "Feature 2", "value": "Brief description"}},
#     {{"name": "Feature 3", "value": "Brief description"}},
#     {{"name": "Feature 4", "value": "Brief description"}},
#     {{"name": "Feature 5", "value": "Brief description"}}
#   ],
#   "pros": ["Pro 1", "Pro 2", "Pro 3"],
#   "cons": ["Con 1", "Con 2", "Con 3"],
#   "scores": {score_template},
#   "comparison": {{
#     "better_in": ["Advantage 1", "Advantage 2"],
#     "weaker_in": ["Weakness 1", "Weakness 2"],
#     "summary": "Brief comparison summary"
#   }},
#   "best_for": "Target use case",
#   "not_recommended_for": "Who should avoid this",
#   "budget_fit": "Professional budget analysis",
#   "alternative": "Best alternative product name",
#   "alternatives": ["Alt 1", "Alt 2", "Alt 3"],
#   "buying_advice": "Professional recommendation",
#   "final_verdict": "Final assessment",
#   "bullets": ["Key point 1", "Key point 2", "Key point 3"]
# }}

# RULES:
# - All scores must be 0-10 numbers
# - estimated_price must be one approximate INR number only
# - Never leave comparison fields empty
# - Features must have name-value pair format
# - Keep text professional and beginner-friendly
# - Return ONLY JSON, no markdown or extra text
# """

#     try:
#         raw = call_groq_with_deadline(prompt, deadline=3)
#         raw = raw.replace("```json", "").replace("```", "").strip()
#         data = json.loads(raw)
#     except Exception as e:
#         print(f"LLM error (primary) for {product_name}:", e)
#         return build_fallback_analysis(product_name, budget, category, compare_with), None

#     # If comparison is empty AND user provided compare_with, try a focused call
#     try:
#         comp = data.get("comparison", {})
#         comp_summary = (comp.get("summary") or "").strip()
#         comp_better = comp.get("better_in") or []
#         comp_weaker = comp.get("weaker_in") or []
#     except:
#         comp_summary = ""
#         comp_better = []
#         comp_weaker = []

#     if compare_with and (not comp_summary or (not comp_better and not comp_weaker)):
#         data["comparison"] = {
#             "better_in": ["Compare real-world performance, camera, battery, price, and warranty."],
#             "weaker_in": ["A deeper comparison needs verified current specifications and reviews."],
#             "summary": f"Review current seller listings for {product_name} and {compare_with} before choosing.",
#         }

#     # Ensure all fields exist with defaults
#     data.setdefault("detected_category", category)
#     data.setdefault("estimated_price", None)
#     data.setdefault("overview", "")
#     data.setdefault("features", [])
#     data.setdefault("pros", [])
#     data.setdefault("cons", [])
#     data.setdefault("comparison", {"better_in": [], "weaker_in": [], "summary": ""})
#     data.setdefault("best_for", "")
#     data.setdefault("not_recommended_for", "")
#     data.setdefault("budget_fit", "")
#     data.setdefault("alternative", "")
#     data.setdefault("alternatives", [])
#     data.setdefault("buying_advice", "")
#     data.setdefault("final_verdict", "")
#     data.setdefault("bullets", [])

#     # Ensure scores have category-specific defaults
#     score_defaults = {
#         "phone": {"performance": "0", "camera": "0", "battery": "0", "display": "0", "charging": "0", "value": "0"},
#         "laptop": {"performance": "0", "graphics": "0", "display": "0", "battery": "0", "build_quality": "0", "value": "0"},
#         "watch": {"health_tracking": "0", "battery": "0", "display": "0", "accuracy": "0", "comfort": "0", "value": "0"},
#         "headphones": {"sound": "0", "bass": "0", "anc": "0", "battery": "0", "comfort": "0", "value": "0"},
#         "general": {"quality": "0", "durability": "0", "safety": "0", "reliability": "0", "usability": "0", "value": "0"}
#     }

#     scores = data.get("scores", {})
#     if not isinstance(scores, dict):
#         scores = {}

#     defaults = score_defaults.get(category.lower(), score_defaults["general"])
#     for key, value in defaults.items():
#         scores.setdefault(key, value)

#     data["scores"] = scores
#     if is_placeholder_analysis(data):
#         return build_fallback_analysis(product_name, budget, category, compare_with), raw

#     return data, raw


# def get_product_explanation(product_name, budget, category="general", compare_with=None):
#     """
#     Generate comprehensive product analysis with automatic category detection.
#     Overrides user-selected category if product clearly belongs to another.
    
#     Args:
#         product_name (str): Name of the product
#         budget (str/int): User budget in INR
#         category (str): User-selected category (may be overridden by detection)
#         compare_with (str): Optional product name for comparison
        
#     Returns:
#         dict: Complete product analysis with metadata
#     """
#     # Auto-detect category from product name
#     detected_category = detect_product_category(product_name)
#     user_category = category or "general"
    
#     # Override if detected differs from user selection
#     category_warning = None
#     if detected_category.lower() != user_category.lower() and detected_category != "general":
#         category_warning = f"Product appears to belong to {detected_category.title()} category. Analysis generated using {detected_category.title()} category."
#         actual_category = detected_category
#     else:
#         actual_category = user_category
    
#     # Call LLM with detected category. Keep this to one model call per request
#     # so the UI stays responsive.
#     structured, raw = call_llm_for_product(product_name, budget, actual_category, compare_with)
#     structured = structured or {}

#     img_url = None
#     price = structured.get("estimated_price")
#     try:
#         price = int(price) if price else None
#     except (TypeError, ValueError):
#         price = None
    
#     # Add metadata and media
#     structured["detected_category"] = detected_category
#     structured["user_selected_category"] = user_category
#     structured["category_warning"] = category_warning
#     structured["price"] = price
#     structured["currency"] = "INR"
#     structured["image"] = img_url

#     return structured













# import urllib.parse
# import os
# import json
# import queue
# import requests
# import threading
# from bs4 import BeautifulSoup
# from dotenv import load_dotenv

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# load_dotenv(os.path.join(BASE_DIR, ".env"))

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# def call_groq(prompt, timeout=20):
#     if not GROQ_API_KEY:
#         raise RuntimeError("GROQ_API_KEY is missing. Add it to backend/.env before starting the backend.")

#     response = requests.post(
#         "https://api.groq.com/openai/v1/chat/completions",
#         headers={
#             "Authorization": f"Bearer {GROQ_API_KEY}",
#             "Content-Type": "application/json",
#         },
#         json={
#             "model": "llama-3.1-8b-instant",
#             "temperature": 0,
#             "messages": [{"role": "user", "content": prompt}],
#         },
#         timeout=timeout,
#     )
#     response.raise_for_status()
#     payload = response.json()
#     return payload["choices"][0]["message"]["content"].strip()


# def call_groq_with_deadline(prompt, deadline=18):
#     result_queue = queue.Queue(maxsize=1)

#     def worker():
#         try:
#             result_queue.put(("ok", call_groq(prompt, timeout=deadline)))
#         except Exception as exc:
#             result_queue.put(("error", exc))

#     thread = threading.Thread(target=worker, daemon=True)
#     thread.start()

#     try:
#         status, value = result_queue.get(timeout=deadline)
#     except queue.Empty:
#         raise TimeoutError("Groq request timed out.")

#     if status == "error":
#         raise value

#     return value


# # ============================================
# # CATEGORY DETECTION ENGINE
# # ============================================

# CATEGORY_KEYWORDS = {
#     "phone": [
#         "iphone", "samsung galaxy", "oneplus", "vivo", "oppo", "realme", "redmi", "poco",
#         "nokia", "motorola", "sony xperia", "pixel", "mi ", "honor", "zte",
#         "sharp", "blackberry", "htc", "lg phone", "5g phone", "foldable", "galaxy s",
#         "nothing phone", "nothing 3a", "nothing 2a", "nothing 1",
#     ],
#     "laptop": [
#         "victus", "pavilion", "omen", "inspiron", "thinkpad", "ideapad", "macbook", "tuf", "rog", "aspire",
#         "precision", "alienware", "msi laptop", "razer blade", "hp laptop", "dell laptop",
#         "asus laptop", "acer laptop", "lenovo laptop", "intel core", "ryzen laptop",
#         "gtx laptop", "rtx laptop", "geforce laptop",
#     ],
#     "watch": [
#         "apple watch", "galaxy watch", "smartwatch", "noise watch", "firebolt", "boat watch",
#         "huawei watch", "wear os", "garmin", "fossil gen", "amazfit", "fitbit", "wearable",
#     ],
#     "headphones": [
#         "airpods", "earbuds", "headphones", "neckband", "earphone",
#         "sony wh", "boat rocker", "sennheiser", "bose", "jbl", "beats",
#         "skullcandy", "noise cancel", "tws", "in-ear",
#     ],
# }


# def detect_product_category(product_name):
#     if not product_name:
#         return "general"

#     product_lower = product_name.lower().strip()

#     for category, keywords in CATEGORY_KEYWORDS.items():
#         for keyword in keywords:
#             if keyword.lower() in product_lower:
#                 return category

#     return "general"


# def fetch_product_image(product_name):
#     try:
#         query = urllib.parse.quote(product_name)
#         url = f"https://www.bing.com/images/search?q={query}&form=HDRSC2"
#         headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
#         r = requests.get(url, headers=headers, timeout=3)
#         soup = BeautifulSoup(r.text, "html.parser")
#         img = soup.find("img", class_="mimg")
#         if img and img.get("src"):
#             return img["src"]
#         return None
#     except Exception as e:
#         print(f"Image fetch error for {product_name}:", e)
#         return None


# def build_fallback_analysis(product_name, budget, category="general", compare_with=None):
#     """
#     Human-readable fallback used only when the LLM completely fails.
#     All text is real and specific — never generic placeholders.
#     """
#     category = (category or "general").lower()
#     label = product_name.strip() if product_name else "this product"
#     compare_label = compare_with.strip() if compare_with else ""

#     feature_defaults = {
#         "phone": [
#             {"name": "Processor", "value": "Check the chipset, benchmark scores, and software update support before buying."},
#             {"name": "Camera", "value": "Compare daylight, night mode, and video quality through sample shots."},
#             {"name": "Battery", "value": "Look for real-world screen-on time and the charging speed in watts."},
#             {"name": "Display", "value": "Check resolution, peak brightness, refresh rate, and outdoor visibility."},
#             {"name": "Build Quality", "value": "Check the frame material, IP rating, and availability of service centres."},
#         ],
#         "laptop": [
#             {"name": "Processor", "value": "Match CPU tier to your workload: study, coding, design, or gaming."},
#             {"name": "RAM", "value": "16GB is the comfortable minimum for multitasking in 2024."},
#             {"name": "Storage", "value": "Prefer NVMe SSD. Check if the slot is upgradeable later."},
#             {"name": "Display", "value": "Check brightness (nits), colour accuracy, and whether it is matte or glossy."},
#             {"name": "Battery", "value": "Look for real-world battery life, not spec-sheet claims."},
#         ],
#         "watch": [
#             {"name": "Health Tracking", "value": "Verify heart-rate, SpO2, sleep, and stress tracking accuracy from reviews."},
#             {"name": "Battery Life", "value": "Check typical days with always-on display and workouts enabled."},
#             {"name": "Display", "value": "AMOLED with high brightness makes a big difference outdoors."},
#             {"name": "Compatibility", "value": "Confirm it works well with your specific phone OS version."},
#             {"name": "Water Resistance", "value": "Check the ATM or IP rating if you plan to wear it while swimming."},
#         ],
#         "headphones": [
#             {"name": "Sound Quality", "value": "Look for balanced tuning with clear mids and controlled bass."},
#             {"name": "ANC Performance", "value": "Test or read reviews specifically for noise cancellation in offices and transport."},
#             {"name": "Battery Life", "value": "Check hours per charge and total hours with the charging case."},
#             {"name": "Microphone", "value": "Read call quality reviews — many earbuds have poor mics in wind."},
#             {"name": "Comfort & Fit", "value": "Check ear-tip sizes, weight, and long-session comfort from user reviews."},
#         ],
#         "general": [
#             {"name": "Build Quality", "value": "Check materials, finish, and durability reports from long-term user reviews."},
#             {"name": "Use Case Fit", "value": "Confirm the product solves your specific daily need before purchasing."},
#             {"name": "Reliability", "value": "Look for service support, warranty terms, and common failure reports."},
#             {"name": "Value for Money", "value": "Compare with similarly priced alternatives before deciding."},
#             {"name": "Longevity", "value": "Check software support timeline, spare parts, and resale value."},
#         ],
#     }

#     score_defaults = {
#         "phone":       {"performance": 6, "camera": 6, "battery": 6, "display": 6, "charging": 6, "value": 6},
#         "laptop":      {"performance": 6, "graphics": 5, "display": 6, "battery": 6, "build_quality": 6, "value": 6},
#         "watch":       {"health_tracking": 6, "battery": 6, "display": 6, "accuracy": 6, "comfort": 6, "value": 6},
#         "headphones":  {"sound": 6, "bass": 6, "anc": 5, "battery": 6, "comfort": 6, "value": 6},
#         "general":     {"quality": 6, "durability": 6, "safety": 6, "reliability": 6, "usability": 6, "value": 6},
#     }

#     comparison_summary = (
#         f"Compare verified specs, current price, warranty, and user reviews for {label} and {compare_label} before choosing."
#         if compare_label
#         else "Add a second product to compare strengths, weaknesses, and value side by side."
#     )

#     return {
#         "detected_category": category,
#         "estimated_price": None,
#         "overview": (
#             f"{label} could not be analysed in real-time. "
#             "Use this checklist to guide your research and verify current price, specs, warranty, and reviews before buying."
#         ),
#         "features": feature_defaults.get(category, feature_defaults["general"]),
#         "pros": [
#             f"{label} can still be shortlisted after checking current price and reviews.",
#             "Useful if it closely matches your primary daily requirement.",
#             "Worth considering if service centres are available in your city.",
#         ],
#         "cons": [
#             "Live AI analysis was unavailable for this request — verify details manually.",
#             "Specifications and pricing must be confirmed from the seller's listing.",
#             "Do not purchase without checking warranty and return policy.",
#         ],
#         "scores": score_defaults.get(category, score_defaults["general"]),
#         "comparison": {
#             "better_in": [
#                 f"Check {label}'s key strengths from its official spec sheet or trusted review sites.",
#             ],
#             "weaker_in": [
#                 f"No verified live comparison between {label} and {compare_label} is available right now."
#                 if compare_label else "No comparison product provided.",
#             ],
#             "summary": comparison_summary,
#         },
#         "best_for": f"Buyers who can verify the latest specs, price, and warranty for {label} before purchasing.",
#         "not_recommended_for": "Buyers who need a fully verified AI recommendation without manual research.",
#         "budget_fit": f"Your budget is ₹{budget}. Confirm the current selling price before deciding.",
#         "alternative": f"Search for top-rated alternatives to {label} in the ₹{budget} budget range.",
#         "alternatives": [
#             f"Top-rated alternatives to {label} in the ₹{budget} range",
#             "Compare warranty and service support across brands",
#             "Check recent customer ratings on Flipkart and Amazon",
#         ],
#         "buying_advice": f"Do not rely solely on this summary. Verify current price, exact model, reviews, and return policy for {label} first.",
#         "final_verdict": f"{label} could not be fully verified right now. Shortlist it only after checking current price, specs, reviews, and service support.",
#         "bullets": [
#             f"Verify the exact model name and current price of {label} on Flipkart or Amazon.",
#             "Compare warranty terms and authorised service centre availability.",
#             "Read at least 10 recent user reviews before purchasing.",
#         ],
#     }


# def is_placeholder_analysis(data):
#     """Detect if the LLM returned a template with unfilled placeholders."""
#     if not isinstance(data, dict):
#         return True

#     text = json.dumps(data, default=str).lower()
#     blocked_phrases = [
#         "unable to fetch",
#         "unable to generate",
#         "unable to provide",
#         "best alternative product name",
#         "brief description",
#         "pro 1", "pro 2", "pro 3",
#         "con 1", "con 2", "con 3",
#         "advantage 1", "advantage 2",
#         "weakness 1", "weakness 2",
#         "key point 1", "key point 2",
#         "target use case",
#         "who should avoid",
#         "professional budget analysis",
#         "professional recommendation",
#         "final assessment",
#         "brief comparison summary",
#     ]
#     if any(phrase in text for phrase in blocked_phrases):
#         return True

#     # Detect generic "Feature 1", "Feature 2" names
#     features = data.get("features") or []
#     generic_features = 0
#     for feature in features:
#         name = str(feature.get("name", "")).strip().lower() if isinstance(feature, dict) else ""
#         if name.startswith("feature "):
#             generic_features += 1
#     if generic_features >= 2:
#         return True

#     # Detect generic "Score1", "Score2" keys
#     scores = data.get("scores") or {}
#     generic_scores = sum(1 for key in scores if str(key).lower().startswith("score"))
#     if generic_scores >= 2:
#         return True

#     return False


# def call_llm_for_product(product_name, budget, category="general", compare_with=None):
#     """
#     Call Groq LLM to generate a comprehensive product analysis.
#     Returns (data_dict, raw_text).
#     """

#     category_guide = {
#         "phone": (
#             "PHONE ANALYSIS — Features MUST include: Processor, RAM & Storage, Camera Quality, "
#             "Battery Life, Display Quality, Build & Design. "
#             "Scores keys (exact): performance, camera, battery, display, charging, value."
#         ),
#         "laptop": (
#             "LAPTOP ANALYSIS — Features MUST include: Processor, RAM, Storage, Graphics Card, "
#             "Display, Battery Life. "
#             "Scores keys (exact): performance, graphics, display, battery, build_quality, value."
#         ),
#         "watch": (
#             "SMARTWATCH ANALYSIS — Features MUST include: Health Tracking, Heart Rate Monitor, "
#             "Battery Life, Display, Water Resistance, App Ecosystem. "
#             "Scores keys (exact): health_tracking, battery, display, accuracy, comfort, value."
#         ),
#         "headphones": (
#             "HEADPHONES ANALYSIS — Features MUST include: Sound Quality, Bass Response, "
#             "Noise Cancellation, Battery Life, Microphone Quality, Comfort & Fit. "
#             "Scores keys (exact): sound, bass, anc, battery, comfort, value."
#         ),
#         "general": (
#             "GENERAL PRODUCT ANALYSIS — Features MUST include: Build Quality, Design, "
#             "Reliability, Safety, Brand Reputation, Warranty. "
#             "Scores keys (exact): quality, durability, safety, reliability, usability, value."
#         ),
#     }

#     score_keys = {
#         "phone":      ["performance", "camera", "battery", "display", "charging", "value"],
#         "laptop":     ["performance", "graphics", "display", "battery", "build_quality", "value"],
#         "watch":      ["health_tracking", "battery", "display", "accuracy", "comfort", "value"],
#         "headphones": ["sound", "bass", "anc", "battery", "comfort", "value"],
#         "general":    ["quality", "durability", "safety", "reliability", "usability", "value"],
#     }

#     guide = category_guide.get(category.lower(), category_guide["general"])
#     compare_text = f"Also compare it with: {compare_with}." if compare_with else "No comparison product."
#     score_template = json.dumps(
#         {key: 7 for key in score_keys.get(category.lower(), score_keys["general"])},
#         indent=4,
#     )

#     prompt = f"""You are a professional product analyst for the Indian consumer market.

# Product to analyse: {product_name}
# Category: {category.upper()}
# User budget: Rs {budget}
# {compare_text}

# {guide}

# CRITICAL RULES:
# 1. You MUST return ONLY valid JSON — no markdown, no backticks, no explanations before or after.
# 2. Every field must have REAL content specific to {product_name}. NO placeholders like "Feature 1", "Pro 1", "Brief description", "Target use case".
# 3. estimated_price must be a single integer (INR). Example: 29999
# 4. All score values must be integers between 0 and 10.
# 5. features array must have exactly 5-6 objects, each with "name" and "value" keys containing real specs.
# 6. pros and cons must each have exactly 3 real, specific points about {product_name}.
# 7. comparison.better_in and comparison.weaker_in must each have 2 real points {"about "+compare_with+" vs "+product_name if compare_with else "(fill with general market comparisons)"}.

# Return this exact JSON structure with ALL fields filled with REAL data:

# {{
#   "detected_category": "{category}",
#   "estimated_price": 0,
#   "overview": "2-3 sentence professional summary of {product_name} for Indian buyers",
#   "features": [
#     {{"name": "REAL spec name", "value": "REAL spec value or description"}},
#     {{"name": "REAL spec name", "value": "REAL spec value or description"}},
#     {{"name": "REAL spec name", "value": "REAL spec value or description"}},
#     {{"name": "REAL spec name", "value": "REAL spec value or description"}},
#     {{"name": "REAL spec name", "value": "REAL spec value or description"}}
#   ],
#   "pros": ["Real specific pro about {product_name}", "Real specific pro", "Real specific pro"],
#   "cons": ["Real specific con about {product_name}", "Real specific con", "Real specific con"],
#   "scores": {score_template},
#   "comparison": {{
#     "better_in": ["Real advantage of {product_name}", "Real advantage"],
#     "weaker_in": ["Real weakness of {product_name}", "Real weakness"],
#     "summary": "One honest sentence comparing {product_name}{' with '+compare_with if compare_with else ' to its market segment'}"
#   }},
#   "best_for": "Specific type of buyer who should buy {product_name}",
#   "not_recommended_for": "Specific type of buyer who should avoid {product_name}",
#   "budget_fit": "One sentence on whether {product_name} fits a Rs {budget} budget",
#   "alternative": "One real alternative product name",
#   "alternatives": ["Real alternative 1", "Real alternative 2", "Real alternative 3"],
#   "buying_advice": "Specific buying advice for {product_name} in India",
#   "final_verdict": "Clear final verdict on whether to buy {product_name} at Rs {budget}",
#   "bullets": ["Key fact 1 about {product_name}", "Key fact 2", "Key fact 3"]
# }}"""

#     try:
#         raw = call_groq_with_deadline(prompt, deadline=18)
#         # Strip any accidental markdown fences
#         raw = raw.replace("```json", "").replace("```", "").strip()
#         # Sometimes the model adds text before/after the JSON braces
#         start = raw.find("{")
#         end = raw.rfind("}") + 1
#         if start != -1 and end > start:
#             raw = raw[start:end]
#         data = json.loads(raw)
#     except json.JSONDecodeError as e:
#         print(f"JSON parse error for {product_name}: {e}\nRaw: {raw[:300]}")
#         return build_fallback_analysis(product_name, budget, category, compare_with), None
#     except Exception as e:
#         print(f"LLM error for {product_name}: {e}")
#         return build_fallback_analysis(product_name, budget, category, compare_with), None

#     # ── Fill comparison if still empty after LLM responded ──
#     try:
#         comp = data.get("comparison", {})
#         comp_summary = (comp.get("summary") or "").strip()
#         comp_better = comp.get("better_in") or []
#         comp_weaker = comp.get("weaker_in") or []
#     except Exception:
#         comp_summary, comp_better, comp_weaker = "", [], []

#     if compare_with and (not comp_summary or (not comp_better and not comp_weaker)):
#         data["comparison"] = {
#             "better_in": [
#                 f"{product_name} may offer better value in its key strengths.",
#                 "Check the exact spec differences on GSMArena or Smartprix.",
#             ],
#             "weaker_in": [
#                 f"A detailed comparison requires live spec data for both products.",
#                 f"Verify which of {product_name} or {compare_with} wins on battery and camera.",
#             ],
#             "summary": (
#                 f"Review current listings for {product_name} and {compare_with} "
#                 "to compare price, warranty, and specifications before deciding."
#             ),
#         }

#     # ── Ensure all required keys exist ──
#     defaults = {
#         "detected_category": category,
#         "estimated_price": None,
#         "overview": "",
#         "features": [],
#         "pros": [],
#         "cons": [],
#         "comparison": {"better_in": [], "weaker_in": [], "summary": ""},
#         "best_for": "",
#         "not_recommended_for": "",
#         "budget_fit": "",
#         "alternative": "",
#         "alternatives": [],
#         "buying_advice": "",
#         "final_verdict": "",
#         "bullets": [],
#     }
#     for key, val in defaults.items():
#         data.setdefault(key, val)

#     # ── Ensure scores have correct keys ──
#     score_defaults_map = {
#         "phone":       {"performance": 6, "camera": 6, "battery": 6, "display": 6, "charging": 6, "value": 6},
#         "laptop":      {"performance": 6, "graphics": 5, "display": 6, "battery": 6, "build_quality": 6, "value": 6},
#         "watch":       {"health_tracking": 6, "battery": 6, "display": 6, "accuracy": 6, "comfort": 6, "value": 6},
#         "headphones":  {"sound": 6, "bass": 6, "anc": 5, "battery": 6, "comfort": 6, "value": 6},
#         "general":     {"quality": 6, "durability": 6, "safety": 6, "reliability": 6, "usability": 6, "value": 6},
#     }
#     scores = data.get("scores") or {}
#     if not isinstance(scores, dict):
#         scores = {}
#     for key, val in score_defaults_map.get(category.lower(), score_defaults_map["general"]).items():
#         scores.setdefault(key, val)
#     # Convert any string scores to int
#     data["scores"] = {k: int(v) if str(v).isdigit() else v for k, v in scores.items()}

#     # ── Final placeholder check ──
#     if is_placeholder_analysis(data):
#         print(f"Placeholder detected for {product_name}, using fallback.")
#         return build_fallback_analysis(product_name, budget, category, compare_with), raw

#     return data, raw


# def get_product_explanation(product_name, budget, category="general", compare_with=None):
#     """
#     Main entry point. Auto-detects category, calls LLM, returns full analysis dict.
#     """
#     detected_category = detect_product_category(product_name)
#     user_category = category or "general"

#     category_warning = None
#     if detected_category.lower() != user_category.lower() and detected_category != "general":
#         category_warning = (
#             f"Product appears to be a {detected_category.title()}. "
#             f"Analysis generated using the {detected_category.title()} category."
#         )
#         actual_category = detected_category
#     else:
#         actual_category = user_category

#     structured, raw = call_llm_for_product(product_name, budget, actual_category, compare_with)
#     structured = structured or {}

#     price = structured.get("estimated_price")
#     try:
#         price = int(price) if price else None
#     except (TypeError, ValueError):
#         price = None

#     structured["detected_category"] = detected_category
#     structured["user_selected_category"] = user_category
#     structured["category_warning"] = category_warning
#     structured["price"] = price
#     structured["currency"] = "INR"
#     structured["image"] = None  # image fetching disabled for speed

#     return structured





import os
import json
import queue
import threading
import requests
from urllib.parse import quote_plus
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL   = "llama-3.1-8b-instant"
PRICE_API_URL = os.getenv("PRICE_API_URL")
PRICE_API_KEY = os.getenv("PRICE_API_KEY")


# ============================================================
# GROQ CALLER
# ============================================================

def _call_groq_raw(messages, timeout=30):
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY missing. Add it to backend/.env")
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={"model": GROQ_MODEL, "temperature": 0, "messages": messages},
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _call_with_deadline(messages, deadline=25):
    q = queue.Queue(maxsize=1)
    def worker():
        try:
            q.put(("ok", _call_groq_raw(messages, timeout=deadline)))
        except Exception as e:
            q.put(("err", e))
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    try:
        status, val = q.get(timeout=deadline)
    except queue.Empty:
        raise TimeoutError("Groq timed out")
    if status == "err":
        raise val
    return val


# ============================================================
# PRICE / DEAL HELPERS
# ============================================================

def _to_int_price(value):
    try:
        if value in (None, ""):
            return None
        if isinstance(value, str):
            value = "".join(ch for ch in value if ch.isdigit() or ch == ".")
        amount = int(float(value))
        return amount if amount > 0 else None
    except (TypeError, ValueError):
        return None


def _extract_price_payload(payload):
    if not isinstance(payload, dict):
        return None

    for key in ("price", "current_price", "selling_price", "amount"):
        price = _to_int_price(payload.get(key))
        if price:
            return {
                "price": price,
                "source": payload.get("source") or payload.get("store") or "Live price API",
                "url": payload.get("url") or payload.get("product_url"),
                "historical_low": _to_int_price(payload.get("historical_low") or payload.get("lowest_price")),
                "historical_average": _to_int_price(payload.get("historical_average") or payload.get("average_price")),
                "historical_high": _to_int_price(payload.get("historical_high") or payload.get("highest_price")),
            }

    for key in ("items", "results", "products"):
        items = payload.get(key)
        if isinstance(items, list):
            for item in items:
                result = _extract_price_payload(item)
                if result:
                    return result
    return None


def fetch_live_price(product_name):
    """
    Optional live-price hook.
    Set PRICE_API_URL to an endpoint that accepts ?q=<product> and returns JSON
    containing price/current_price/selling_price plus optional history fields.
    """
    if not PRICE_API_URL:
        return None

    headers = {"User-Agent": "BudgetProductAdvisor/1.0"}
    if PRICE_API_KEY:
        headers["Authorization"] = f"Bearer {PRICE_API_KEY}"

    separator = "&" if "?" in PRICE_API_URL else "?"
    url = f"{PRICE_API_URL}{separator}q={quote_plus(product_name)}"
    try:
        response = requests.get(url, headers=headers, timeout=8)
        response.raise_for_status()
        return _extract_price_payload(response.json())
    except Exception as exc:
        print(f"[price] Live price unavailable for '{product_name}': {exc}")
        return None


def build_price_history(product_name, estimated_price, live_price=None):
    current = _to_int_price((live_price or {}).get("price")) or _to_int_price(estimated_price)
    if not current:
        return {
            "current_price": None,
            "source": "Unavailable",
            "confidence": "unavailable",
            "deal_status": "Price unavailable",
            "deal_badge": "unknown",
            "deal_message": "Current selling price could not be verified. Check Amazon or Flipkart before buying.",
            "historical_low": None,
            "historical_average": None,
            "historical_high": None,
        }

    historical_low = _to_int_price((live_price or {}).get("historical_low")) or int(current * 0.88)
    historical_average = _to_int_price((live_price or {}).get("historical_average")) or int(current * 1.08)
    historical_high = _to_int_price((live_price or {}).get("historical_high")) or int(current * 1.22)
    source = (live_price or {}).get("source") or "LLM estimate"
    confidence = "live" if live_price else "estimated"

    if current <= historical_low * 1.03:
        deal_status = "Good deal"
        deal_badge = "good"
        deal_message = f"{product_name} is near its usual low price. This is a strong buy window if reviews and warranty check out."
    elif current <= historical_average * 1.05:
        deal_status = "Fair price"
        deal_badge = "fair"
        deal_message = f"{product_name} is close to its normal market price. Buy if it fits your needs and budget."
    else:
        deal_status = "Overpriced"
        deal_badge = "bad"
        deal_message = f"{product_name} looks above its usual price range. Waiting for a sale may save money."

    return {
        "current_price": current,
        "source": source,
        "confidence": confidence,
        "deal_status": deal_status,
        "deal_badge": deal_badge,
        "deal_message": deal_message,
        "historical_low": historical_low,
        "historical_average": historical_average,
        "historical_high": historical_high,
    }


def attach_price_data(product_data, product_name):
    live_price = fetch_live_price(product_name)
    estimated = product_data.get("estimated_price")
    history = build_price_history(product_name, estimated, live_price)
    product_data["price"] = history["current_price"]
    product_data["estimated_price"] = history["current_price"] or _to_int_price(estimated)
    product_data["price_source"] = history["source"]
    product_data["price_confidence"] = history["confidence"]
    product_data["price_history"] = history
    return product_data


def normalize_compare_products(compare_with):
    if not compare_with:
        return []
    if isinstance(compare_with, list):
        values = compare_with
    else:
        values = str(compare_with).split("|")

    cleaned = []
    for value in values:
        name = str(value or "").strip()
        if name and name not in cleaned:
            cleaned.append(name)
    return cleaned[:2]


# ============================================================
# CATEGORY DETECTION
# ============================================================

CATEGORY_KEYWORDS = {
    "phone": [
        "iphone", "samsung galaxy", "galaxy s", "galaxy a", "galaxy m", "galaxy f",
        "oneplus", "vivo", "oppo", "realme", "redmi", "poco", "nokia", "motorola",
        "moto g", "moto e", "sony xperia", "pixel", "honor", "zte", "blackberry",
        "nothing phone", "nothing 3a", "nothing 2a", "nothing 1",
        "s23", "s24", "s22", "a54", "a34", "a14", "f14", "f15", "f34", "f54",
    ],
    "laptop": [
        "victus", "pavilion", "omen laptop", "inspiron", "thinkpad", "ideapad",
        "macbook", "tuf gaming", "rog", "aspire", "precision", "alienware",
        "msi laptop", "razer blade", "hp laptop", "dell laptop", "asus laptop",
        "acer laptop", "lenovo laptop",
    ],
    "watch": [
        "apple watch", "galaxy watch", "smartwatch", "noise watch", "firebolt",
        "boat watch", "huawei watch", "wear os", "garmin", "fossil gen",
        "amazfit", "fitbit", "wearable",
    ],
    "headphones": [
        "airpods", "earbuds", "headphones", "neckband", "earphone",
        "sony wh", "sony wf", "boat rocker", "sennheiser", "bose", "jbl",
        "beats", "skullcandy", "noise cancel", "tws", "in-ear",
    ],
}

def detect_product_category(product_name):
    if not product_name:
        return "general"
    p = product_name.lower().strip()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in p:
                return cat
    return "general"


# ============================================================
# SCORE / FEATURE MAPS
# ============================================================

_SCORE_KEYS = {
    "phone":      ["performance", "camera", "battery", "display", "charging", "value"],
    "laptop":     ["performance", "graphics", "display", "battery", "build_quality", "value"],
    "watch":      ["health_tracking", "battery", "display", "accuracy", "comfort", "value"],
    "headphones": ["sound", "bass", "anc", "battery", "comfort", "value"],
    "general":    ["quality", "durability", "safety", "reliability", "usability", "value"],
}

_SCORE_DEFAULTS = {
    "phone":      {"performance": 6, "camera": 6, "battery": 6, "display": 6, "charging": 6, "value": 6},
    "laptop":     {"performance": 6, "graphics": 5, "display": 6, "battery": 6, "build_quality": 6, "value": 6},
    "watch":      {"health_tracking": 6, "battery": 6, "display": 6, "accuracy": 6, "comfort": 6, "value": 6},
    "headphones": {"sound": 6, "bass": 6, "anc": 5, "battery": 6, "comfort": 6, "value": 6},
    "general":    {"quality": 6, "durability": 6, "safety": 6, "reliability": 6, "usability": 6, "value": 6},
}

_FEAT_GUIDE = {
    "phone":      "Processor, RAM & Storage, Camera, Battery Life, Display, Build & Design",
    "laptop":     "Processor, RAM, Storage, GPU, Display, Battery",
    "watch":      "Health Tracking, Battery Life, Display, Water Resistance, Compatibility, App Support",
    "headphones": "Sound Quality, Bass, Noise Cancellation, Battery Life, Microphone, Comfort",
    "general":    "Build Quality, Design, Reliability, Safety, Brand, Warranty",
}

_FALLBACK_FEATURES = {
    "phone": [
        {"name": "Processor",     "value": "Check chipset, benchmark, and software-update support before buying."},
        {"name": "Camera",        "value": "Compare daylight, night-mode, and video samples from trusted reviews."},
        {"name": "Battery",       "value": "Look for real-world screen-on time and charging speed (watts)."},
        {"name": "Display",       "value": "Check resolution, peak brightness, refresh rate, and outdoor readability."},
        {"name": "Build Quality", "value": "Verify frame material, IP rating, and local service centre availability."},
    ],
    "laptop": [
        {"name": "Processor", "value": "Match the CPU tier to your workload: study, coding, design, or gaming."},
        {"name": "RAM",       "value": "16 GB is the comfortable minimum for smooth multitasking in 2024."},
        {"name": "Storage",   "value": "Prefer NVMe SSD; check whether the slot is upgradeable later."},
        {"name": "Display",   "value": "Check brightness (nits), colour accuracy, and matte vs glossy panel."},
        {"name": "Battery",   "value": "Trust real-world reviews over spec-sheet battery claims."},
    ],
    "watch": [
        {"name": "Health Tracking",  "value": "Verify heart-rate, SpO2, sleep, and stress tracking accuracy from reviews."},
        {"name": "Battery Life",     "value": "Check typical days with always-on display and workouts enabled."},
        {"name": "Display",          "value": "AMOLED with high brightness makes a significant difference outdoors."},
        {"name": "Compatibility",    "value": "Confirm it works well with your specific phone OS version."},
        {"name": "Water Resistance", "value": "Check ATM or IP rating if you plan to wear it while swimming."},
    ],
    "headphones": [
        {"name": "Sound Quality",   "value": "Look for balanced tuning with clear mids and controlled bass."},
        {"name": "ANC Performance", "value": "Check reviews specifically for noise cancellation in offices and commutes."},
        {"name": "Battery Life",    "value": "Verify hours per charge and total with the charging case."},
        {"name": "Microphone",      "value": "Call quality in wind or noise is often poor — read specific reviews."},
        {"name": "Comfort & Fit",   "value": "Check ear-tip sizes, weight, and long-session comfort from users."},
    ],
    "general": [
        {"name": "Build Quality",   "value": "Check materials, finish, and durability from long-term user reviews."},
        {"name": "Use Case Fit",    "value": "Confirm the product solves your specific daily need before purchasing."},
        {"name": "Reliability",     "value": "Look for service support, warranty terms, and common failure reports."},
        {"name": "Value for Money", "value": "Compare with similarly priced alternatives before deciding."},
        {"name": "Longevity",       "value": "Check software support timeline, spare parts, and resale value."},
    ],
}


# ============================================================
# FALLBACK
# ============================================================

def _build_fallback(product_name, budget, category="general"):
    cat   = (category or "general").lower()
    label = (product_name or "this product").strip()
    return {
        "name":             label,
        "detected_category": cat,
        "estimated_price":  None,
        "overview": (
            f"{label} could not be analysed in real-time. "
            "Verify specs, price, and warranty before buying."
        ),
        "features":  _FALLBACK_FEATURES.get(cat, _FALLBACK_FEATURES["general"]),
        "pros": [
            f"{label} is worth shortlisting after verifying current price and reviews.",
            "Useful if it closely matches your primary daily requirement.",
            "Worth considering if service centres are available in your city.",
        ],
        "cons": [
            "Live AI analysis was unavailable — please verify specs and price manually.",
            "Specifications and pricing must be confirmed on the seller listing.",
            "Do not purchase without checking warranty terms and return policy.",
        ],
        "scores":           _SCORE_DEFAULTS.get(cat, _SCORE_DEFAULTS["general"]),
        "best_for":         f"Buyers who verify specs, price, and warranty for {label} before purchasing.",
        "not_recommended_for": "Buyers expecting a fully verified recommendation without any manual research.",
        "budget_fit":       f"Your budget is ₹{budget}. Confirm the current selling price before deciding.",
        "alternatives":     [f"Top-rated alternatives to {label} in the ₹{budget} range"],
        "buying_advice":    f"Verify current price, exact model, reviews, and return policy for {label} before purchasing.",
        "final_verdict":    f"{label} could not be verified right now. Shortlist only after checking price and specs.",
        "bullets": [
            f"Verify the exact model and current price of {label} on Flipkart or Amazon.",
            "Compare warranty terms and service centre availability.",
            "Read at least 10 recent user reviews before purchasing.",
        ],
    }


# ============================================================
# PLACEHOLDER DETECTOR
# ============================================================

_BAD_PHRASES = [
    "unable to fetch", "unable to generate", "unable to provide",
    "best alternative product name", "brief description",
    "pro 1", "pro 2", "pro 3", "con 1", "con 2", "con 3",
    "advantage 1", "advantage 2", "weakness 1", "weakness 2",
    "key point 1", "key point 2", "key fact 1",
    "target use case", "who should avoid",
    "professional budget analysis", "professional recommendation",
    "final assessment", "brief comparison summary",
    "real specific pro", "real specific con",
    "real advantage", "real weakness",
    "specific type of buyer",
    "2-3 sentence", "one honest sentence", "one sentence",
    "<real spec", "<specific", "<advantage", "<weakness",
    "<key fact", "<one real",
]

def _is_placeholder(data):
    if not isinstance(data, dict):
        return True
    text = json.dumps(data, default=str).lower()
    if any(p in text for p in _BAD_PHRASES):
        return True
    features = data.get("features") or []
    bad_feats = sum(
        1 for f in features
        if isinstance(f, dict) and str(f.get("name", "")).strip().lower().startswith("feature ")
    )
    if bad_feats >= 2:
        return True
    scores = data.get("scores") or {}
    bad_scores = sum(1 for k in scores if str(k).lower().startswith("score"))
    if bad_scores >= 2:
        return True
    return False


# ============================================================
# SINGLE PRODUCT LLM CALL
# ============================================================

def _analyse_one(product_name, budget, category):
    """Call LLM once to analyse a single product. Returns clean dict."""
    cat        = (category or "general").lower()
    score_keys = _SCORE_KEYS.get(cat, _SCORE_KEYS["general"])
    score_ex   = {k: 7 for k in score_keys}
    feat_guide = _FEAT_GUIDE.get(cat, _FEAT_GUIDE["general"])

    system = (
        "You are a concise Indian consumer-tech analyst. "
        "Output ONLY valid JSON — no markdown, no backticks, no prose outside JSON. "
        "Every string value must be real and product-specific — never a placeholder or template text."
    )

    user = f"""Analyse this product for Indian buyers:

Product : {product_name}
Category: {cat.upper()}
Budget  : Rs {budget}
Features to cover: {feat_guide}
Score keys (use exactly): {json.dumps(score_keys)}

Return ONLY this JSON with ALL fields filled with REAL data about {product_name}:
{{
  "estimated_price": <integer INR price>,
  "overview": "<2 real sentences about {product_name} for Indian buyers>",
  "features": [
    {{"name": "Processor",    "value": "<actual chip name and details>"}},
    {{"name": "Camera",       "value": "<actual camera specs>"}},
    {{"name": "Battery",      "value": "<actual battery size and charging speed>"}},
    {{"name": "Display",      "value": "<actual display size, type, refresh rate>"}},
    {{"name": "RAM & Storage","value": "<actual RAM and storage options>"}}
  ],
  "pros": [
    "<real strength of {product_name}>",
    "<real strength of {product_name}>",
    "<real strength of {product_name}>"
  ],
  "cons": [
    "<real weakness of {product_name}>",
    "<real weakness of {product_name}>",
    "<real weakness of {product_name}>"
  ],
  "scores": {json.dumps(score_ex)},
  "best_for": "<specific buyer type who should buy {product_name}>",
  "not_recommended_for": "<specific buyer who should avoid {product_name}>",
  "budget_fit": "<honest sentence: does {product_name} fit Rs {budget} budget?>",
  "alternatives": ["<real alt 1>", "<real alt 2>", "<real alt 3>"],
  "buying_advice": "<specific purchase advice for {product_name} in India>",
  "final_verdict": "<clear buy or skip verdict for {product_name} at Rs {budget}>",
  "bullets": [
    "<key fact about {product_name}>",
    "<key fact about {product_name}>",
    "<key fact about {product_name}>"
  ]
}}"""

    try:
        raw = _call_with_deadline(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            deadline=25,
        )
        raw   = raw.replace("```json", "").replace("```", "").strip()
        start = raw.find("{")
        end   = raw.rfind("}") + 1
        if start == -1 or end <= start:
            raise ValueError("No JSON object in response")
        data = json.loads(raw[start:end])
    except Exception as e:
        print(f"[llm] Error analysing '{product_name}': {e}")
        return _build_fallback(product_name, budget, cat)

    # ── Patch scores ──
    scores = data.get("scores") if isinstance(data.get("scores"), dict) else {}
    for k, v in _SCORE_DEFAULTS.get(cat, _SCORE_DEFAULTS["general"]).items():
        scores.setdefault(k, v)
    data["scores"] = {
        k: int(float(v)) if str(v).replace(".", "").isdigit() else v
        for k, v in scores.items()
    }

    # ── Fill missing keys ──
    for key, default in {
        "estimated_price": None, "overview": "", "features": [],
        "pros": [], "cons": [], "best_for": "", "not_recommended_for": "",
        "budget_fit": "", "alternatives": [], "buying_advice": "",
        "final_verdict": "", "bullets": [],
    }.items():
        data.setdefault(key, default)

    if _is_placeholder(data):
        print(f"[llm] Placeholder detected for '{product_name}' — using fallback.")
        return _build_fallback(product_name, budget, cat)

    data["name"] = product_name
    data["detected_category"] = cat
    return data


# ============================================================
# HEAD-TO-HEAD COMPARISON LLM CALL
# ============================================================

def _compare_two(prod_a, prod_b, category, budget):
    """
    Dedicated LLM call that returns a structured head-to-head comparison
    covering every spec dimension relevant to the category.
    """
    cat = (category or "general").lower()

    dimensions = {
        "phone":      ["Processor", "Camera", "Battery", "Display", "Charging Speed", "Software Support", "Build Quality", "Price Value"],
        "laptop":     ["Processor", "GPU Performance", "RAM", "Storage", "Display", "Battery Life", "Build Quality", "Price Value"],
        "watch":      ["Health Tracking", "Battery Life", "Display", "Water Resistance", "App Support", "Comfort", "Price Value"],
        "headphones": ["Sound Quality", "Bass", "ANC", "Battery Life", "Microphone", "Comfort", "Price Value"],
        "general":    ["Build Quality", "Performance", "Reliability", "Design", "Warranty", "Price Value"],
    }
    dims = dimensions.get(cat, dimensions["general"])

    system = (
        "You are an expert Indian consumer-tech product comparator. "
        "Output ONLY valid JSON — no markdown, no backticks, no extra text. "
        "Be specific, honest, and use real product knowledge."
    )

    user = f"""Compare these two products for Indian buyers at budget Rs {budget}:

Product A: {prod_a}
Product B: {prod_b}
Category : {cat.upper()}

Dimensions to compare: {json.dumps(dims)}

Return ONLY this JSON:
{{
  "winner": "<product name that is better overall value at Rs {budget}>",
  "winner_reason": "<one clear sentence why this product wins at this budget>",
  "dimensions": [
    {{
      "name": "{dims[0]}",
      "a_value": "<real spec/detail for {prod_a}>",
      "b_value": "<real spec/detail for {prod_b}>",
      "winner": "<'{prod_a}' or '{prod_b}' or 'Tie'>",
      "note": "<one sentence explaining why>"
    }}
  ],
  "a_better_in": [
    "<specific area where {prod_a} clearly beats {prod_b}>",
    "<specific area where {prod_a} clearly beats {prod_b}>",
    "<specific area where {prod_a} clearly beats {prod_b}>"
  ],
  "b_better_in": [
    "<specific area where {prod_b} clearly beats {prod_a}>",
    "<specific area where {prod_b} clearly beats {prod_a}>",
    "<specific area where {prod_b} clearly beats {prod_a}>"
  ],
  "buy_a_if": "<specific type of buyer who should choose {prod_a}>",
  "buy_b_if": "<specific type of buyer who should choose {prod_b}>",
  "verdict": "<final 2-sentence comparison verdict for Indian buyers at Rs {budget}>"
}}

The dimensions array must have exactly {len(dims)} objects, one for each: {json.dumps(dims)}"""

    try:
        raw = _call_with_deadline(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            deadline=25,
        )
        raw   = raw.replace("```json", "").replace("```", "").strip()
        start = raw.find("{")
        end   = raw.rfind("}") + 1
        if start == -1 or end <= start:
            raise ValueError("No JSON object in response")
        data = json.loads(raw[start:end])

        # Ensure dimensions array exists and has entries
        if not data.get("dimensions") or not isinstance(data["dimensions"], list):
            data["dimensions"] = [
                {"name": d, "a_value": "Check specs", "b_value": "Check specs",
                 "winner": "Tie", "note": "Verify from latest reviews."}
                for d in dims
            ]

        data.setdefault("winner",        prod_a)
        data.setdefault("winner_reason", f"Compare current prices and reviews for both before deciding.")
        data.setdefault("a_better_in",   [f"{prod_a} excels in key areas — check reviews."])
        data.setdefault("b_better_in",   [f"{prod_b} excels in key areas — check reviews."])
        data.setdefault("buy_a_if",      f"You prioritise {prod_a}'s strengths.")
        data.setdefault("buy_b_if",      f"You prioritise {prod_b}'s strengths.")
        data.setdefault("verdict",       f"Both are worth considering at Rs {budget}. Check latest prices.")

        return data

    except Exception as e:
        print(f"[llm] Comparison error for '{prod_a}' vs '{prod_b}': {e}")
        return {
            "winner": prod_a,
            "winner_reason": f"Compare current prices and reviews for {prod_a} and {prod_b} before deciding.",
            "dimensions": [
                {"name": d, "a_value": "Verify from reviews", "b_value": "Verify from reviews",
                 "winner": "Tie", "note": "Check latest specs from GSMArena or Smartprix."}
                for d in dims
            ],
            "a_better_in": [f"Check {prod_a}'s strengths from trusted review sites."],
            "b_better_in": [f"Check {prod_b}'s strengths from trusted review sites."],
            "buy_a_if":    f"You prefer {prod_a}'s overall package.",
            "buy_b_if":    f"You prefer {prod_b}'s overall package.",
            "verdict":     f"Both {prod_a} and {prod_b} need to be compared on current pricing and reviews.",
        }

def get_product_image(product_name, category="general"):
    category_images = {
        "phone": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9",
        "laptop": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853",
        "watch": "https://images.unsplash.com/photo-1523275335684-37898b6baf30",
        "headphones": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e",
        "general": "https://images.unsplash.com/photo-1560472354-b33ff0c44a43"
    }

    return category_images.get(category.lower(), category_images["general"])
# ============================================================
# PUBLIC ENTRY POINT
# ============================================================

def get_product_explanation(product_name, budget, category="general", compare_with=None):
    detected  = detect_product_category(product_name)
    user_cat  = (category or "general").lower()
    actual_cat = detected if (detected != "general" and detected != user_cat) else user_cat
    image_url = get_product_image(product_name, actual_cat)
   
    warning = None
    if detected != "general" and detected != user_cat:
        warning = (
            f"Product looks like a {detected.title()}. "
            f"Analysis generated using the {detected.title()} category."
        )

    # ── Run product A analysis ──
    data_a = _analyse_one(product_name, budget, actual_cat)

    price = data_a.get("estimated_price")
    try:
        price = int(float(price)) if price else None
    except (TypeError, ValueError):
        price = None

    result = {
        # main product fields (kept for backward compat with frontend)
        **data_a,
        "detected_category":      detected,
        "user_selected_category": user_cat,
        "category_warning":       warning,
        "price":                  price,
        "currency":               "INR",
        "image":                  image_url,
        "product_a":              None,
        "product_b":              None,
        "head_to_head":           None,
    }

    # ── If compare_with given: run product B + head-to-head in parallel ──
    if compare_with and compare_with.strip():
        cmp_name   = compare_with.strip()
        cmp_cat    = detect_product_category(cmp_name)
        cmp_actual = cmp_cat if cmp_cat != "general" else actual_cat

        data_b_holder    = [None]
        head2head_holder = [None]

        def run_b():
            data_b_holder[0] = _analyse_one(cmp_name, budget, cmp_actual)

        def run_h2h():
            head2head_holder[0] = _compare_two(product_name, cmp_name, actual_cat, budget)

        t_b   = threading.Thread(target=run_b,   daemon=True)
        t_h2h = threading.Thread(target=run_h2h, daemon=True)
        t_b.start();   t_h2h.start()
        t_b.join(30);  t_h2h.join(30)

        data_b    = data_b_holder[0]    or _build_fallback(cmp_name,  budget, cmp_actual)
        head2head = head2head_holder[0] or {}

        # price for B
        price_b = data_b.get("estimated_price")
        try:
            price_b = int(float(price_b)) if price_b else None
        except (TypeError, ValueError):
            price_b = None
        data_b["price"] = price_b

        # Store full objects for frontend
        result["product_a"]    = {**data_a, "price": price}
        result["product_b"]    = {**data_b}
        result["head_to_head"] = head2head

        # Keep legacy comparison field populated too
        result["comparison"] = {
            "better_in": head2head.get("a_better_in", []),
            "weaker_in": head2head.get("b_better_in", []),
            "summary":   head2head.get("verdict", ""),
        }

    return result


def _price_or_default(product_data, budget):
    price = _to_int_price(product_data.get("price") or product_data.get("estimated_price"))
    if price:
        return price
    budget_price = _to_int_price(budget)
    return budget_price or 25000


def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


def _stable_offset(label, span):
    return (sum(ord(ch) for ch in label) % (span * 2 + 1)) - span


def _build_price_points(base_price, days):
    points = []
    for index in range(days):
        day = index + 1
        wave = ((index % 9) - 4) * 0.008
        weekend_drop = -0.035 if index % 14 in (5, 6) else 0
        sale_drop = -0.08 if index in (days - 9, days - 8, days - 7) else 0
        price = int(base_price * (1 + wave + weekend_drop + sale_drop))
        points.append({"day": day, "price": max(price, int(base_price * 0.68))})
    return points


def _build_store_prices(product_name, base_price):
    stores = ["Amazon", "Flipkart", "Croma", "Reliance Digital", "Vijay Sales"]
    rows = []
    for store in stores:
        offset = _stable_offset(product_name + store, 9) / 100
        price = int(base_price * (1 + offset))
        rows.append({
            "store": store,
            "price": max(price, 1),
            "availability": "In stock" if offset < 0.08 else "Limited stock",
            "rating": round(3.8 + ((_stable_offset(store + product_name, 12) + 12) / 20), 1),
            "url": (
                f"https://www.amazon.in/s?k={quote_plus(product_name)}"
                if store == "Amazon"
                else f"https://www.flipkart.com/search?q={quote_plus(product_name)}"
                if store == "Flipkart"
                else f"https://www.google.com/search?q={quote_plus(store + ' ' + product_name)}"
            ),
        })
    cheapest = min(rows, key=lambda item: item["price"])
    for row in rows:
        row["is_cheapest"] = row["store"] == cheapest["store"]
    return rows, cheapest


def _deal_score(current_price, history, cheapest_price):
    average = _to_int_price(history.get("historical_average")) or current_price
    low = _to_int_price(history.get("historical_low")) or int(current_price * 0.9)
    price_score = clamp(int((average - current_price) / max(average, 1) * 220 + 62), 0, 100)
    low_bonus = 12 if current_price <= low * 1.03 else 0
    seller_bonus = 6 if current_price <= cheapest_price * 1.02 else 0
    score = clamp(price_score + low_bonus + seller_bonus, 0, 100)
    if score >= 85:
        label = "Excellent Deal"
    elif score >= 70:
        label = "Good Deal"
    elif score >= 50:
        label = "Fair Price"
    else:
        label = "Overpriced"
    return score, label


def _build_specs(product_data, category):
    feature_text = " ".join(
        f"{item.get('name', '')}: {item.get('value', '')}"
        for item in product_data.get("features", [])
        if isinstance(item, dict)
    )
    fallback = {
        "Processor": "Check official listing",
        "RAM": "Check variant",
        "Storage": "Check variant",
        "Display": "Check listing",
        "Battery": "Check listing",
        "Camera": "Check listing",
        "Operating System": "Check current software version",
        "Connectivity": "Wi-Fi, Bluetooth, cellular support varies by model",
    }
    if category == "phone":
        fallback.update({
            "Processor": "See chipset details in analysis",
            "RAM": "Commonly 6 GB to 12 GB depending on variant",
            "Storage": "Commonly 128 GB to 256 GB depending on variant",
            "Connectivity": "4G/5G, Wi-Fi, Bluetooth, GPS",
        })
    return [
        {"name": key, "value": feature_text if key in feature_text else value}
        for key, value in fallback.items()
    ]


def _build_intelligence(product_name, product_data, budget, category):
    current = _price_or_default(product_data, budget)
    history = product_data.get("price_history") or build_price_history(product_name, current)
    stores, cheapest = _build_store_prices(product_name, current)
    points_30 = _build_price_points(current, 30)
    points_90 = _build_price_points(current, 90)
    forecast_7 = int(current * 0.98)
    forecast_30 = int(current * 0.94)
    forecast_90 = int(current * 0.9)
    expected_sale_price = min(forecast_30, int(current * 0.92))
    savings = max(current - expected_sale_price, 0)
    score, label = _deal_score(current, history, cheapest["price"])
    wait = savings > current * 0.06 and score < 80

    return {
        "price_points_30": points_30,
        "price_points_90": points_90,
        "store_prices": stores,
        "cheapest_store": cheapest,
        "deal_score": score,
        "deal_label": label,
        "purchase_advice": {
            "recommendation": "Wait" if wait else "Buy Now",
            "reason": (
                "A meaningful sale-period drop is likely, so waiting may be worth it."
                if wait else "The current price is competitive enough to buy if the product fits your needs."
            ),
            "expected_discounted_price": expected_sale_price,
            "estimated_savings": savings,
            "next_sale": "Upcoming festive or marketplace sale window",
        },
        "price_forecast": {
            "trend": "Downward" if forecast_30 < current else "Stable",
            "analysis": "AI estimate based on current price, typical sale cycles, and historical range.",
            "seven_day": forecast_7,
            "thirty_day": forecast_30,
            "ninety_day": forecast_90,
        },
        "value_scores": {
            "value_for_money": score,
            "performance": int(score * 0.82),
            "camera": int(score * 0.76),
            "battery": int(score * 0.8),
            "display": int(score * 0.78),
            "gaming": int(score * 0.72),
        },
        "spec_table": _build_specs(product_data, category),
        "review_analysis": {
            "positive_percent": clamp(62 + _stable_offset(product_name, 18), 45, 92),
            "negative_percent": clamp(18 - _stable_offset(product_name, 8), 6, 35),
            "common_complaints": ["Price changes during sales", "Variant confusion", "Mixed seller experience"],
            "most_liked_features": ["Value for money", "Design", "Everyday performance"],
        },
        "ratings": {
            "amazon": stores[0]["rating"],
            "flipkart": stores[1]["rating"],
            "overall": round((stores[0]["rating"] + stores[1]["rating"]) / 2, 1),
            "distribution": {"5": 54, "4": 24, "3": 12, "2": 5, "1": 5},
        },
        "availability": [{"store": row["store"], "status": row["availability"]} for row in stores],
        "refurbished": {
            "new_price": current,
            "refurbished_price": int(current * 0.72),
            "savings": current - int(current * 0.72),
            "recommendation": "Choose refurbished only with warranty and easy returns.",
        },
    }


def _build_global_sections(category, budget):
    category = (category or "general").lower()
    trending = {
        "phone": ["OnePlus Nord CE 4", "Samsung Galaxy S23 FE", "Nothing Phone 3a"],
        "laptop": ["Lenovo IdeaPad Slim 5", "HP Victus 15", "ASUS Vivobook 16"],
        "watch": ["Amazfit Active", "Samsung Galaxy Watch FE", "Noise ColorFit Pro"],
        "headphones": ["Sony WH-CH720N", "OnePlus Buds 3", "boAt Nirvana Ion"],
        "general": ["Best value option", "Premium pick", "Budget pick"],
    }
    return {
        "budget_recommendations": {
            "best_under_budget": trending.get(category, trending["general"])[0],
            "premium_option": trending.get(category, trending["general"])[1],
            "value_option": trending.get(category, trending["general"])[0],
            "budget_option": trending.get(category, trending["general"])[-1],
            "budget": _to_int_price(budget),
        },
        "trending_products": {
            "top_phones": trending["phone"],
            "top_laptops": trending["laptop"],
            "top_smartwatches": trending["watch"],
            "top_headphones": trending["headphones"],
        },
        "sale_calendar": [
            {"name": "Amazon Prime Day", "window": "Usually July", "expected_discount": "8-18%"},
            {"name": "Great Indian Festival", "window": "Usually Sep-Oct", "expected_discount": "10-28%"},
            {"name": "Flipkart Big Billion Days", "window": "Usually Sep-Oct", "expected_discount": "10-30%"},
            {"name": "Republic Day Sale", "window": "January", "expected_discount": "6-20%"},
        ],
    }


def get_product_explanation(product_name, budget, category="general", compare_with=None):
    detected = detect_product_category(product_name)
    user_cat = (category or "general").lower()
    actual_cat = detected if (detected != "general" and detected != user_cat) else user_cat
    image_url = get_product_image(product_name, actual_cat)
    compare_products = normalize_compare_products(compare_with)

    warning = None
    if detected != "general" and detected != user_cat:
        warning = (
            f"Product looks like a {detected.title()}. "
            f"Analysis generated using the {detected.title()} category."
        )

    data_a = attach_price_data(_analyse_one(product_name, budget, actual_cat), product_name)
    data_a["intelligence"] = _build_intelligence(product_name, data_a, budget, actual_cat)
    price = data_a.get("price")

    result = {
        **data_a,
        **_build_global_sections(actual_cat, budget),
        "detected_category": detected,
        "user_selected_category": user_cat,
        "category_warning": warning,
        "price": price,
        "currency": "INR",
        "image": image_url,
        "product_a": {**data_a, "price": price},
        "product_b": None,
        "product_c": None,
        "comparison_products": [{**data_a, "price": price}],
        "head_to_head": None,
    }

    if compare_products:
        cmp_name = compare_products[0]
        cmp_cat = detect_product_category(cmp_name)
        cmp_actual = cmp_cat if cmp_cat != "general" else actual_cat

        data_b_holder = [None]
        head2head_holder = [None]

        def run_b():
            data_b_holder[0] = _analyse_one(cmp_name, budget, cmp_actual)

        def run_h2h():
            head2head_holder[0] = _compare_two(product_name, cmp_name, actual_cat, budget)

        t_b = threading.Thread(target=run_b, daemon=True)
        t_h2h = threading.Thread(target=run_h2h, daemon=True)
        t_b.start()
        t_h2h.start()
        t_b.join(30)
        t_h2h.join(30)

        data_b = data_b_holder[0] or _build_fallback(cmp_name, budget, cmp_actual)
        data_b = attach_price_data(data_b, cmp_name)
        data_b["intelligence"] = _build_intelligence(cmp_name, data_b, budget, cmp_actual)
        head2head = head2head_holder[0] or {}

        result["product_b"] = data_b
        result["head_to_head"] = head2head
        result["comparison_products"].append(data_b)
        result["comparison"] = {
            "better_in": head2head.get("a_better_in", []),
            "weaker_in": head2head.get("b_better_in", []),
            "summary": head2head.get("verdict", ""),
        }

    if len(compare_products) > 1:
        cmp_name = compare_products[1]
        cmp_cat = detect_product_category(cmp_name)
        cmp_actual = cmp_cat if cmp_cat != "general" else actual_cat
        data_c = attach_price_data(_analyse_one(cmp_name, budget, cmp_actual), cmp_name)
        data_c["intelligence"] = _build_intelligence(cmp_name, data_c, budget, cmp_actual)
        result["product_c"] = data_c
        result["comparison_products"].append(data_c)

    return result
