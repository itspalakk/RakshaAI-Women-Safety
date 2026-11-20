import geocoder

def get_location():
    """
    Returns estimated coordinates and region based on IP lookup.
    Used as an immediate fallback when HTML5 GPS is unavailable or blocked.
    """
    try:
        g = geocoder.ip('me')
        if g.ok and g.latlng:
            return {
                "lat": float(g.latlng[0]),
                "lng": float(g.latlng[1]),
                "city": getattr(g, 'city', '') or 'Indore',
                "state": getattr(g, 'state', '') or 'Madhya Pradesh',
                "country": getattr(g, 'country', '') or 'India',
                "address": getattr(g, 'address', '') or f"{getattr(g, 'city', '')}, {getattr(g, 'state', '')}"
            }
    except Exception as exc:
        print(f"[location_module] IP Geolocation lookup warning: {exc}")
    
    # Sensible default to Indore central hub if completely offline
    return {
        "lat": 22.7196,
        "lng": 75.8577,
        "city": "Indore",
        "state": "Madhya Pradesh",
        "country": "India",
        "address": "Indore, Madhya Pradesh"
    }
