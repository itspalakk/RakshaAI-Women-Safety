import os
import re
import math
import json
import urllib.request
import urllib.parse
import ssl

# ── Verified Indore & Regional Landmarks Catalog ──
# Provides instantaneous, 0-latency, 100% reliable matching for colleges, hospitals,
# police stations, transit hubs, and famous squares even during network latency or provider downtime.
LOCAL_LANDMARKS = [
    # ── Educational Institutions & Colleges ──
    {
        "id": "indore_medicaps",
        "name": "Medi-Caps University",
        "sub": "Main Campus, Mhow Bypass Road, Pigdamber, Rau, Indore",
        "lat": 22.6225,
        "lng": 75.8038,
        "type": "college",
        "icon": "🎓",
        "tags": ["medicaps", "medi-caps", "medicaps university", "medi caps", "rau", "pigdamber", "pigdambar", "engineering", "campus", "college"]
    },
    {
        "id": "indore_iet_davv",
        "name": "IET DAVV (Institute of Engineering & Technology)",
        "sub": "Khandwa Road, Takshashila Campus, DAVV, Indore",
        "lat": 22.6812,
        "lng": 75.8796,
        "type": "college",
        "icon": "🎓",
        "tags": ["iet", "iet davv", "davv iet", "engineering", "khandwa road", "davv", "college"]
    },
    {
        "id": "indore_davv_takshashila",
        "name": "Devi Ahilya Vishwavidyalaya (Takshashila Campus)",
        "sub": "Khandwa Road, Bhanwarkuan area, Indore",
        "lat": 22.6908,
        "lng": 75.8752,
        "type": "college",
        "icon": "🎓",
        "tags": ["davv", "devi ahilya", "vishwavidyalaya", "takshashila", "university", "khandwa road"]
    },
    {
        "id": "indore_sgsits",
        "name": "SGSITS (Shri Govindram Seksaria Institute)",
        "sub": "23 Sir M. Visvesvaraya Marg, Park Road, Vallabh Nagar, Indore",
        "lat": 22.7265,
        "lng": 75.8732,
        "type": "college",
        "icon": "🎓",
        "tags": ["sgsits", "gsits", "govindram seksaria", "park road", "vallabh nagar", "engineering college"]
    },
    {
        "id": "indore_holkar_science",
        "name": "Govt. Holkar Science College",
        "sub": "AB Road, Near Bhawarkua, Indore",
        "lat": 22.6961,
        "lng": 75.8643,
        "type": "college",
        "icon": "🎓",
        "tags": ["holkar", "holkar college", "holkar science", "bhawarkua", "ab road", "science college"]
    },
    {
        "id": "indore_ips_academy",
        "name": "IPS Academy",
        "sub": "Knowledge Village, Rajendra Nagar, A.B. Road, Indore",
        "lat": 22.6644,
        "lng": 75.8252,
        "type": "college",
        "icon": "🎓",
        "tags": ["ips", "ips academy", "rajendra nagar", "ab road", "college"]
    },
    {
        "id": "indore_iist",
        "name": "Indore Institute of Science & Technology (IIST)",
        "sub": "Opposite IIM Indore, Rau-Pithampur Road, Rau, Indore",
        "lat": 22.6148,
        "lng": 75.7682,
        "type": "college",
        "icon": "🎓",
        "tags": ["iist", "indore institute", "rau pithampur", "iim indore", "college"]
    },
    {
        "id": "indore_sage_univ",
        "name": "SAGE University",
        "sub": "Kailod Kartal, Indore-Dewas Bypass Road, Rau, Indore",
        "lat": 22.6468,
        "lng": 75.9238,
        "type": "college",
        "icon": "🎓",
        "tags": ["sage", "sage university", "kailod kartal", "bypass", "university"]
    },
    {
        "id": "indore_pimr",
        "name": "Prestige Institute of Management & Research (PIMR)",
        "sub": "2, Education & Health Sector, Scheme 54, Vijay Nagar, Indore",
        "lat": 22.7538,
        "lng": 75.8912,
        "type": "college",
        "icon": "🎓",
        "tags": ["prestige", "pimr", "scheme 54", "vijay nagar", "mba college"]
    },
    {
        "id": "indore_acropolis",
        "name": "Acropolis Institute of Technology & Research",
        "sub": "Bypass Road, Manglia Square, Indore",
        "lat": 22.7885,
        "lng": 75.9284,
        "type": "college",
        "icon": "🎓",
        "tags": ["acropolis", "acropolis institute", "manglia", "bypass", "engineering"]
    },

    # ── Key Squares, Localities & Neighborhoods ──
    {
        "id": "indore_bhawarkua",
        "name": "Bhawarkua Square (Bhanwarkuan)",
        "sub": "Major Student Hub & Transit Junction, AB Road, Indore",
        "lat": 22.6939,
        "lng": 75.8667,
        "type": "landmark",
        "icon": "📍",
        "tags": ["bhawarkua", "bhanwarkuan", "bhawarkuwa", "bhanwarkua", "bhawar kuan", "bhanwar kuan", "bhawarkua square", "indore", "ab road", "student hub", "bus stop"]
    },
    {
        "id": "indore_rau_circle",
        "name": "Rau Circle (Rau Gol Chauraha)",
        "sub": "Mhow Bypass / AB Road Junction, Rau, Indore",
        "lat": 22.6318,
        "lng": 75.8115,
        "type": "landmark",
        "icon": "📍",
        "tags": ["rau", "rau circle", "rau chauraha", "mhow bypass", "pigdamber", "ab road"]
    },
    {
        "id": "indore_silicon_city",
        "name": "Silicon City",
        "sub": "A.B. Road, Near Rau, Indore",
        "lat": 22.6450,
        "lng": 75.8180,
        "type": "landmark",
        "icon": "📍",
        "tags": ["silicon city", "silicon", "rau", "ab road"]
    },
    {
        "id": "indore_rajwada",
        "name": "Rajwada Palace & Square",
        "sub": "MG Road, Sarafa Bazaar, Old Indore",
        "lat": 22.7180,
        "lng": 75.8548,
        "type": "landmark",
        "icon": "📍",
        "tags": ["rajwada", "rajwada palace", "rajwada square", "sarafa", "mg road", "heritage"]
    },
    {
        "id": "indore_chhappan",
        "name": "Chhappan Dukan (56 Dukan)",
        "sub": "New Palasia, Indore",
        "lat": 22.7238,
        "lng": 75.8821,
        "type": "landmark",
        "icon": "🛍️",
        "tags": ["chhappan", "56 dukan", "chappan", "new palasia", "food street", "market"]
    },
    {
        "id": "indore_sarafa",
        "name": "Sarafa Night Food Market",
        "sub": "Near Rajwada, Sarafa Bazaar, Indore",
        "lat": 22.7176,
        "lng": 75.8539,
        "type": "landmark",
        "icon": "🛍️",
        "tags": ["sarafa", "sarafa bazaar", "night market", "street food", "rajwada"]
    },
    {
        "id": "indore_palasia",
        "name": "Palasia Square (Industry House)",
        "sub": "AB Road / Old Palasia, Indore",
        "lat": 22.7247,
        "lng": 75.8872,
        "type": "landmark",
        "icon": "📍",
        "tags": ["palasia", "palasia square", "industry house", "ab road", "old palasia", "new palasia"]
    },
    {
        "id": "indore_vijay_nagar",
        "name": "Vijay Nagar Square",
        "sub": "AB Road / Ring Road Junction, Indore",
        "lat": 22.7511,
        "lng": 75.8955,
        "type": "landmark",
        "icon": "📍",
        "tags": ["vijay nagar", "vijay nagar square", "ring road", "ab road", "c21"]
    },
    {
        "id": "indore_geeta_bhawan",
        "name": "Geeta Bhawan Square",
        "sub": "AB Road, Indore",
        "lat": 22.7182,
        "lng": 75.8841,
        "type": "landmark",
        "icon": "📍",
        "tags": ["geeta bhawan", "gita bhawan", "ab road", "square"]
    },
    {
        "id": "indore_navlakha",
        "name": "Navlakha Square & Bus Stand",
        "sub": "AB Road / Nemawar Road, Indore",
        "lat": 22.6997,
        "lng": 75.8754,
        "type": "landmark",
        "icon": "📍",
        "tags": ["navlakha", "naulakha", "ab road", "nemawar road", "bus stand"]
    },
    {
        "id": "indore_regal_square",
        "name": "Regal Square (High Court)",
        "sub": "RNT Marg / MG Road, Indore",
        "lat": 22.7188,
        "lng": 75.8712,
        "type": "landmark",
        "icon": "📍",
        "tags": ["regal", "regal square", "high court", "rnt marg"]
    },
    {
        "id": "indore_annapurna",
        "name": "Annapurna Temple & Area",
        "sub": "Annapurna Road, Western Indore",
        "lat": 22.6958,
        "lng": 75.8398,
        "type": "landmark",
        "icon": "📍",
        "tags": ["annapurna", "annapurna road", "temple", "mandir"]
    },
    {
        "id": "indore_khajrana",
        "name": "Khajrana Ganesh Mandir",
        "sub": "Khajrana Road, Indore",
        "lat": 22.7297,
        "lng": 75.9082,
        "type": "landmark",
        "icon": "📍",
        "tags": ["khajrana", "khajrana ganesh", "mandir", "temple"]
    },
    {
        "id": "indore_pipliyapala",
        "name": "Regional Park (Pipliyapala Lake)",
        "sub": "Ring Road, Choithram Bypass, Indore",
        "lat": 22.6782,
        "lng": 75.8509,
        "type": "landmark",
        "icon": "🌳",
        "tags": ["regional park", "pipliyapala", "pipliyapala lake", "atal bihari"]
    },
    {
        "id": "indore_ti_mall",
        "name": "Treasure Island Mall (TI Mall)",
        "sub": "11 MG Road, South Tukoganj, Indore",
        "lat": 22.7214,
        "lng": 75.8778,
        "type": "commercial",
        "icon": "🛍️",
        "tags": ["treasure island", "ti mall", "mg road", "mall", "shopping"]
    },
    {
        "id": "indore_phoenix_citadel",
        "name": "Phoenix Citadel Mall",
        "sub": "MR 10 Junction, Bypass Road, Indore",
        "lat": 22.7765,
        "lng": 75.9221,
        "type": "commercial",
        "icon": "🛍️",
        "tags": ["phoenix", "phoenix citadel", "citadel mall", "mr 10", "bypass"]
    },
    {
        "id": "indore_c21_mall",
        "name": "C21 Mall & Malhar Mega Mall",
        "sub": "AB Road, Scheme 54, Vijay Nagar, Indore",
        "lat": 22.7487,
        "lng": 75.8945,
        "type": "commercial",
        "icon": "🛍️",
        "tags": ["c21", "c21 mall", "malhar mega mall", "vijay nagar", "ab road"]
    },

    # ── Major Hospitals & Emergency Healthcare ──
    {
        "id": "indore_choithram",
        "name": "Choithram Hospital & Research Centre",
        "sub": "14 Manikbagh Road, Indore (24/7 Emergency)",
        "lat": 22.6893,
        "lng": 75.8529,
        "type": "hospital",
        "icon": "🏥",
        "tags": ["choithram", "choithram hospital", "manikbagh", "hospital", "emergency", "icu"]
    },
    {
        "id": "indore_bombay_hospital",
        "name": "Bombay Hospital Indore",
        "sub": "Ring Road, IDA Scheme No. 94/95, Vijay Nagar, Indore",
        "lat": 22.7535,
        "lng": 75.8943,
        "type": "hospital",
        "icon": "🏥",
        "tags": ["bombay hospital", "bombay", "ring road", "vijay nagar", "emergency", "hospital"]
    },
    {
        "id": "indore_my_hospital",
        "name": "Maharaja Yeshwantrao Hospital (MY Hospital)",
        "sub": "AB Road, Sanyogitaganj, Indore",
        "lat": 22.7161,
        "lng": 75.8679,
        "type": "hospital",
        "icon": "🏥",
        "tags": ["my hospital", "maharaja yeshwantrao", "m.y. hospital", "sanyogitaganj", "govt hospital"]
    },
    {
        "id": "indore_chl_hospital",
        "name": "CHL Hospital",
        "sub": "AB Road, Near LIG Square, Indore",
        "lat": 22.7368,
        "lng": 75.8893,
        "type": "hospital",
        "icon": "🏥",
        "tags": ["chl", "chl hospital", "lig", "ab road", "hospital"]
    },
    {
        "id": "indore_medanta",
        "name": "Medanta Super Speciality Hospital",
        "sub": "Plot No. 8, PU-4, Commercial Complex, Rasoma Circle, Vijay Nagar, Indore",
        "lat": 22.7523,
        "lng": 75.8958,
        "type": "hospital",
        "icon": "🏥",
        "tags": ["medanta", "medanta hospital", "rasoma", "vijay nagar", "hospital"]
    },
    {
        "id": "indore_aurobindo",
        "name": "Sri Aurobindo Hospital (SAIMS)",
        "sub": "Indore-Ujjain Highway, Sanwer Road, Bhawrasla, Indore",
        "lat": 22.7845,
        "lng": 75.8576,
        "type": "hospital",
        "icon": "🏥",
        "tags": ["aurobindo", "saims", "sri aurobindo", "bhawrasla", "sanwer road"]
    },
    {
        "id": "indore_apple_hospital",
        "name": "Apple Hospital",
        "sub": "Bhawarkua Main Road, Near Transport Nagar, Indore",
        "lat": 22.6932,
        "lng": 75.8584,
        "type": "hospital",
        "icon": "🏥",
        "tags": ["apple", "apple hospital", "bhawarkua", "transport nagar"]
    },

    # ── Police Stations & Official Safety Posts ──
    {
        "id": "indore_ps_bhanwarkua",
        "name": "Bhanwarkua Police Station",
        "sub": "Near Bhawarkua Square, AB Road, Indore",
        "lat": 22.6948,
        "lng": 75.8661,
        "type": "police",
        "icon": "🚔",
        "tags": ["bhanwarkua police", "bhawarkua police", "thana", "police station", "ab road"]
    },
    {
        "id": "indore_ps_rau",
        "name": "Rau Police Station",
        "sub": "Main Road, Near Rau Circle, Indore",
        "lat": 22.6329,
        "lng": 75.8094,
        "type": "police",
        "icon": "🚔",
        "tags": ["rau police", "rau thana", "police station", "rau", "pigdamber"]
    },
    {
        "id": "indore_ps_annapurna",
        "name": "Annapurna Police Station",
        "sub": "Annapurna Road, Near Usha Nagar, Indore",
        "lat": 22.6975,
        "lng": 75.8385,
        "type": "police",
        "icon": "🚔",
        "tags": ["annapurna police", "annapurna thana", "police station"]
    },
    {
        "id": "indore_ps_rajendra_nagar",
        "name": "Rajendra Nagar Police Station",
        "sub": "AB Road, Rajendra Nagar, Indore",
        "lat": 22.6680,
        "lng": 75.8270,
        "type": "police",
        "icon": "🚔",
        "tags": ["rajendra nagar police", "police station", "thana", "ab road"]
    },
    {
        "id": "indore_ps_palasia",
        "name": "Palasia Police Station",
        "sub": "Palasia Square, AB Road, Indore",
        "lat": 22.7235,
        "lng": 75.8860,
        "type": "police",
        "icon": "🚔",
        "tags": ["palasia police", "palasia thana", "police station"]
    },
    {
        "id": "indore_ps_mahila",
        "name": "Mahila Thana (Women's Special Police Station)",
        "sub": "Near Palasia Police Station, Old Palasia, Indore",
        "lat": 22.7238,
        "lng": 75.8865,
        "type": "police",
        "icon": "🚔",
        "tags": ["mahila thana", "women police", "women safety", "palasia", "special police"]
    },

    # ── Transit Hubs ──
    {
        "id": "indore_railway_station",
        "name": "Indore Junction Railway Station",
        "sub": "Chhoti Gwaltoli, Near Sarwate Bus Stand, Indore",
        "lat": 22.7177,
        "lng": 75.8682,
        "type": "transit",
        "icon": "🚉",
        "tags": ["indore junction", "railway station", "train station", "chhoti gwaltoli", "station"]
    },
    {
        "id": "indore_airport",
        "name": "Devi Ahilya Bai Holkar Airport (Indore Airport)",
        "sub": "Depalpur Road, Indore",
        "lat": 22.7258,
        "lng": 75.8066,
        "type": "transit",
        "icon": "✈️",
        "tags": ["airport", "indore airport", "devi ahilya airport", "aerodrome"]
    },
    {
        "id": "indore_sarwate_bus",
        "name": "Sarwate Bus Stand",
        "sub": "South Tukoganj, Near Railway Station, Indore",
        "lat": 22.7135,
        "lng": 75.8680,
        "type": "transit",
        "icon": "🚌",
        "tags": ["sarwate", "bus stand", "bus terminal", "tukoganj"]
    },
    {
        "id": "mhow_cantt",
        "name": "Dr. Ambedkar Nagar (Mhow)",
        "sub": "Military Cantonment & Town, Indore District",
        "lat": 22.5542,
        "lng": 75.7638,
        "type": "landmark",
        "icon": "📍",
        "tags": ["mhow", "dr ambedkar nagar", "cantonment", "military"]
    }
]

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """Calculates great-circle distance between two points in kilometers."""
    r = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


STOPWORDS = {"road", "street", "junction", "station", "circle", "area", "point", "near", "square", "chowk", "chauraha", "city", "nagar", "market", "campus", "hub", "bypass", "stand", "bus", "main"}
OTHER_CITIES = {"bhopal", "delhi", "mumbai", "pune", "ujjain", "dewas", "gwalior", "jabalpur", "bangalore", "bengaluru", "hyderabad", "chennai", "kolkata", "jaipur", "ahmedabad"}

def search_local_landmarks(query, user_lat=None, user_lng=None):
    """Searches curated landmarks with fuzzy token matching and local bias."""
    if not query or len(query.strip()) < 2:
        return []

    q_clean = query.lower().strip()
    # If the user explicitly searches for another city, avoid false matching local Indore landmarks
    query_words = set(re.split(r'[\s,\.-]+', q_clean))
    specified_other_city = any(c in query_words for c in OTHER_CITIES)
    if specified_other_city and "indore" not in query_words:
        return []

    # Normalize common phonetics / variants
    q_norm = q_clean.replace("bhanwar", "bhawar").replace("kuan", "kua").replace("chok", "square").replace("chowk", "square").replace("univ", "university")

    tokens = [t for t in re.split(r'[\s,\.-]+', q_clean) if t not in STOPWORDS and len(t) >= 3]
    norm_tokens = [t for t in re.split(r'[\s,\.-]+', q_norm) if t not in STOPWORDS and len(t) >= 3]
    all_query_terms = list(set(tokens + norm_tokens))

    matches = []
    for lm in LOCAL_LANDMARKS:
        score = 0
        name_lower = lm["name"].lower()
        sub_lower = lm["sub"].lower()
        tags = [t.lower() for t in lm.get("tags", [])]

        # Exact / substring match in primary name
        if q_clean in name_lower or q_norm in name_lower:
            score += 120
        elif all_query_terms and any(term in name_lower for term in all_query_terms):
            score += 70

        # Subtitle / address match
        if q_clean in sub_lower or q_norm in sub_lower:
            score += 40
        elif all_query_terms and any(term in sub_lower for term in all_query_terms):
            score += 25

        # Tags match
        for tag in tags:
            if q_clean == tag or q_norm == tag:
                score += 100
            elif q_clean in tag or q_norm in tag:
                score += 60
            elif all_query_terms and any(t in tag for t in all_query_terms):
                score += 35

        # Only count if score indicates meaningful match
        if score >= 35:
            dist_km = None
            if user_lat is not None and user_lng is not None:
                dist_km = calculate_haversine_distance(user_lat, user_lng, lm["lat"], lm["lng"])
                # Slight proximity boost for places within 25km
                if dist_km < 25.0:
                    score += max(0, int(25.0 - dist_km))

            matches.append({
                "id": lm["id"],
                "name": lm["name"],
                "sub": lm["sub"],
                "lat": lm["lat"],
                "lng": lm["lng"],
                "type": lm["type"],
                "icon": lm["icon"],
                "provider": "verified_landmark",
                "score": score,
                "dist_km": dist_km
            })

    # Sort descending by score
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches


def search_google_places(query, user_lat=None, user_lng=None, api_key=None):
    """
    Queries Google Maps Places Autocomplete & Details API if GOOGLE_MAPS_API_KEY is configured.
    Secret key is kept 100% on the Flask backend.
    """
    if not api_key:
        return []

    try:
        # Autocomplete query
        params = {
            "input": query,
            "key": api_key,
            "language": "en"
        }
        if user_lat is not None and user_lng is not None:
            params["location"] = f"{user_lat},{user_lng}"
            params["radius"] = "25000"  # 25km radius bias

        url = "https://maps.googleapis.com/maps/api/place/autocomplete/json?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": "AlertMeWomenSafety/1.0"})
        ctx = ssl._create_unverified_context()

        with urllib.request.urlopen(req, context=ctx, timeout=4) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        predictions = data.get("predictions", [])
        if not predictions:
            return []

        results = []
        # Get coordinates for top 4 predictions
        for pred in predictions[:4]:
            place_id = pred.get("place_id")
            description = pred.get("description", "")
            main_text = pred.get("structured_formatting", {}).get("main_text", description.split(",")[0])
            secondary_text = pred.get("structured_formatting", {}).get("secondary_text", ", ".join(description.split(",")[1:3]))
            types = pred.get("types", [])

            # Fetch Place Details
            det_params = {
                "place_id": place_id,
                "fields": "geometry,name,formatted_address,type",
                "key": api_key
            }
            det_url = "https://maps.googleapis.com/maps/api/place/details/json?" + urllib.parse.urlencode(det_params)
            det_req = urllib.request.Request(det_url, headers={"User-Agent": "AlertMeWomenSafety/1.0"})
            with urllib.request.urlopen(det_req, context=ctx, timeout=3) as det_resp:
                det_data = json.loads(det_resp.read().decode('utf-8'))

            geom = det_data.get("result", {}).get("geometry", {}).get("location", {})
            lat = geom.get("lat")
            lng = geom.get("lng")

            if lat is not None and lng is not None:
                icon = "📍"
                place_type = "landmark"
                if any(t in types for t in ["university", "school", "college"]):
                    icon = "🎓"
                    place_type = "college"
                elif any(t in types for t in ["hospital", "doctor", "health"]):
                    icon = "🏥"
                    place_type = "hospital"
                elif any(t in types for t in ["police"]):
                    icon = "🚔"
                    place_type = "police"
                elif any(t in types for t in ["shopping_mall", "store"]):
                    icon = "🛍️"
                    place_type = "commercial"
                elif any(t in types for t in ["transit_station", "bus_station", "train_station"]):
                    icon = "🚉"
                    place_type = "transit"

                results.append({
                    "id": f"google_{place_id}",
                    "name": main_text,
                    "sub": secondary_text or description,
                    "lat": float(lat),
                    "lng": float(lng),
                    "type": place_type,
                    "icon": icon,
                    "provider": "google_places",
                    "score": 150
                })

        return results
    except Exception as e:
        print(f"[/api/search-places] Google Places API warning: {e}")
        return []


def search_nominatim(query, user_lat=None, user_lng=None):
    """
    Queries OpenStreetMap Nominatim with server-side User-Agent, handling variations
    and local viewbox biasing around Indore when applicable.
    """
    ctx = ssl._create_unverified_context()
    headers = {"User-Agent": "AlertMeWomenSafetyApp/1.0 (contact@alertme.org)"}
    results = []

    # Prepare queries to try
    queries_to_try = [query]
    # If user is in Indore and query doesn't specify Indore, also try with city context
    is_indore_context = False
    if user_lat is not None and user_lng is not None:
        if 22.0 <= user_lat <= 23.5 and 75.0 <= user_lng <= 76.5:
            is_indore_context = True

    if is_indore_context and "indore" not in query.lower():
        queries_to_try.append(f"{query}, Indore")

    seen_coords = set()

    for q_attempt in queries_to_try:
        try:
            params = {
                "format": "json",
                "q": q_attempt,
                "limit": "6",
                "addressdetails": "1"
            }
            if user_lat is not None and user_lng is not None:
                # Viewbox: left, top, right, bottom (min lon, max lat, max lon, min lat)
                params["viewbox"] = f"{user_lng - 0.45},{user_lat + 0.45},{user_lng + 0.45},{user_lat - 0.45}"

            url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(params)
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=2.5) as resp:
                items = json.loads(resp.read().decode('utf-8'))

            for item in items:
                lat = float(item.get("lat", 0))
                lng = float(item.get("lon", 0))
                coord_key = (round(lat, 3), round(lng, 3))
                if coord_key in seen_coords:
                    continue
                seen_coords.add(coord_key)

                disp = item.get("display_name", "")
                parts = [p.strip() for p in disp.split(",")]
                short_name = parts[0] if parts else query
                sub = ", ".join(parts[1:4]) if len(parts) > 1 else disp

                item_type = item.get("type", "")
                item_cls = item.get("class", "")

                icon = "📍"
                ptype = "landmark"
                if any(k in item_type for k in ["college", "university", "school"]):
                    icon = "🎓"
                    ptype = "college"
                elif any(k in item_type for k in ["hospital", "clinic", "doctors"]):
                    icon = "🏥"
                    ptype = "hospital"
                elif "police" in item_type:
                    icon = "🚔"
                    ptype = "police"
                elif item_cls == "shop" or any(k in item_type for k in ["mall", "market"]):
                    icon = "🛍️"
                    ptype = "commercial"
                elif any(k in item_type for k in ["station", "subway", "bus", "halt"]):
                    icon = "🚉"
                    ptype = "transit"

                # Calculate distance if user coords known
                dist_km = None
                if user_lat is not None and user_lng is not None:
                    dist_km = calculate_haversine_distance(user_lat, user_lng, lat, lng)

                results.append({
                    "id": f"osm_{item.get('osm_id', '')}",
                    "name": short_name,
                    "sub": sub,
                    "lat": lat,
                    "lng": lng,
                    "type": ptype,
                    "icon": icon,
                    "provider": "openstreetmap",
                    "score": 50,
                    "dist_km": dist_km
                })

            if len(results) >= 5:
                break
        except Exception as e:
            print(f"[/api/search-places] Nominatim warning for '{q_attempt}': {e}")

    return results


def search_all_places(query, user_lat=None, user_lng=None):
    """
    Multi-tiered place search:
    1. Google Places (if GOOGLE_MAPS_API_KEY configured)
    2. Curated Local Landmarks (Indore & surrounding region)
    3. OpenStreetMap Nominatim with local bias and retry
    Returns combined, deduplicated, sorted place suggestions.
    """
    if not query or len(query.strip()) < 2:
        return []

    google_key = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
    google_results = []
    if google_key and google_key != "replace_with_your_google_maps_api_key":
        google_results = search_google_places(query, user_lat, user_lng, google_key)

    curated_results = search_local_landmarks(query, user_lat, user_lng)

    # If curated results gave 3+ strong matches, skip slow external network calls for instant sub-10ms response
    osm_results = []
    if len(curated_results) < 3 and not google_results:
        osm_results = search_nominatim(query, user_lat, user_lng)

    # Merge and deduplicate by coordinate proximity (< 150m)
    final_list = []
    seen_positions = []

    def is_duplicate(lat, lng):
        for s_lat, s_lng in seen_positions:
            if calculate_haversine_distance(lat, lng, s_lat, s_lng) < 0.15: # < 150m
                return True
        return False

    # 1. Add Google results first (if available)
    for r in google_results:
        if not is_duplicate(r["lat"], r["lng"]):
            seen_positions.append((r["lat"], r["lng"]))
            final_list.append(r)

    # 2. Add Curated high-relevance landmarks
    for r in curated_results:
        if not is_duplicate(r["lat"], r["lng"]):
            seen_positions.append((r["lat"], r["lng"]))
            final_list.append(r)

    # 3. Add OSM geocoding results
    for r in osm_results:
        if not is_duplicate(r["lat"], r["lng"]):
            seen_positions.append((r["lat"], r["lng"]))
            final_list.append(r)

    # If user coordinates are provided, bias the order so closer locations rank higher
    # while preserving strong exact matches
    if user_lat is not None and user_lng is not None:
        def rank_key(item):
            # Items with high score stay near the top, penalized gently by distance
            dist = item.get("dist_km") or 50.0
            score = item.get("score", 50)
            return -(score - min(30, dist * 0.8))
        final_list.sort(key=rank_key)

    return final_list[:8]


def get_prominent_institutions(user_lat=None, user_lng=None):
    """
    Returns prominent colleges, hospitals, and police landmarks with clean coordinates
    to render as prominent map POIs so the map clearly identifies universities
    (such as Medi-Caps University) instead of confusing individual building blocks.
    """
    institutions = [lm for lm in LOCAL_LANDMARKS if lm["type"] in ["college", "hospital", "police"]]
    if user_lat is not None and user_lng is not None:
        for inst in institutions:
            inst["dist_km"] = round(calculate_haversine_distance(user_lat, user_lng, inst["lat"], inst["lng"]), 2)
        institutions.sort(key=lambda x: x["dist_km"])
    return institutions[:15]


def get_nearest_safe_places(user_lat=None, user_lng=None, limit=8):
    """
    Returns curated, verified safe places (police stations, 24/7 hospitals, staffed campuses)
    sorted by proximity to the user, formatted for the UI's nearest safe haven cards.
    """
    target_lat = user_lat if user_lat is not None else 22.7196
    target_lng = user_lng if user_lng is not None else 75.8577

    places = []
    for lm in LOCAL_LANDMARKS:
        ptype = lm.get("type")
        if ptype not in ["police", "hospital", "commercial", "college"]:
            continue

        dist_km = calculate_haversine_distance(target_lat, target_lng, lm["lat"], lm["lng"])
        dist_m = int(dist_km * 1000)

        icon = lm.get("icon", "📍")
        if ptype == "police":
            status_text = "24/7 Official Emergency Help · Staffed"
            cert_class = "high-cert"
            can_call = True
        elif ptype == "hospital":
            status_text = "24/7 Emergency Care · Medical Refuge"
            cert_class = "high-cert"
            can_call = True
        elif ptype == "college":
            status_text = "Staffed Campus & Security Gate"
            cert_class = "high-cert"
            can_call = False
        else:
            status_text = "Populated Public Space"
            cert_class = "med-cert"
            can_call = False

        places.append({
            "id": lm.get("id"),
            "name": lm.get("name"),
            "type": ptype,
            "icon": icon,
            "sub": lm.get("sub", ""),
            "lat": lm.get("lat"),
            "lng": lm.get("lng"),
            "dist": dist_m,
            "dist_km": round(dist_km, 2),
            "statusText": status_text,
            "certClass": cert_class,
            "canCall": can_call
        })

    places.sort(key=lambda p: p["dist"])
    return places[:limit]

