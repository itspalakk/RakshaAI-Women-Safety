import os
import sys

# ── Ensure UTF-8 output on Windows consoles to prevent charmap UnicodeEncodeError ──
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from flask import Flask, request, jsonify, render_template
from datetime import datetime, timezone
from dotenv import load_dotenv

# ── Load .env FIRST before anything else ──
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

from helpers.alert_module import send_whatsapp_alert
from helpers.textbee_service import send_textbee_sms, check_textbee_connectivity
from helpers.places_module import search_all_places, get_prominent_institutions, get_nearest_safe_places
from helpers.location_module import get_location as get_ip_location
from helpers.voice_module import check_distress_phrase
from config import log_sos_event, get_sos_events, sos_collection

app = Flask(__name__)


# ── CORS — allow browser fetch() from any origin ──
@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin']  = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

@app.route('/send-alert', methods=['OPTIONS'])
def preflight():
    return '', 204


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ping')
def ping():
    tb = check_textbee_connectivity()
    tb_api_key = os.getenv("TEXTBEE_API_KEY", "")
    tb_device  = os.getenv("TEXTBEE_DEVICE_ID", "")
    return jsonify({
        "status":             "ok",
        "message":            "RakshaAI server is running",
        "textbee_connected":  tb["ok"],
        "textbee_message":    tb["message"],
        "textbee_api_key_set":  bool(tb_api_key and not tb_api_key.startswith("replace")),
        "textbee_device_set":   bool(tb_device  and not tb_device.startswith("replace")),
        "database_connected": bool(sos_collection is not None)
    })


@app.route('/api/my-location', methods=['GET'])
def api_my_location():
    """
    Fallback server-side IP geolocation endpoint.
    Called when browser HTML5 geolocation is unavailable, denied, or insecure.
    """
    loc = get_ip_location()
    return jsonify({
        "status": "success",
        "location": loc
    })


@app.route('/api/search-places', methods=['GET'])
def api_search_places():
    """
    Real-world place search endpoint supporting:
    - Google Places API (when GOOGLE_MAPS_API_KEY is configured)
    - Curated Indore & regional institutions, landmarks, colleges, hospitals, and police stations
    - OpenStreetMap Nominatim with local coordinates biasing and retry
    """
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify({"status": "success", "results": []})

    user_lat = request.args.get('lat', type=float)
    user_lng = request.args.get('lon', type=float)
    if user_lng is None:
        user_lng = request.args.get('lng', type=float)

    results = search_all_places(q, user_lat, user_lng)
    return jsonify({
        "status": "success",
        "query": q,
        "count": len(results),
        "results": results
    })


@app.route('/api/institutions', methods=['GET'])
def api_institutions():
    """Returns recognizable colleges, hospitals, and landmarks with exact coordinates."""
    user_lat = request.args.get('lat', type=float)
    user_lng = request.args.get('lon', type=float)
    if user_lng is None:
        user_lng = request.args.get('lng', type=float)

    insts = get_prominent_institutions(user_lat, user_lng)
    return jsonify({
        "status": "success",
        "count": len(insts),
        "institutions": insts
    })


@app.route('/api/nearest-safe-places', methods=['GET'])
def api_nearest_safe_places():
    """
    Returns curated, verified safe places (police stations, hospitals, 24/7 care hubs)
    sorted by proximity to the user's current coordinates.
    """
    user_lat = request.args.get('lat', type=float)
    user_lng = request.args.get('lon', type=float)
    if user_lng is None:
        user_lng = request.args.get('lng', type=float)

    limit = request.args.get('limit', default=8, type=int)
    safe_places = get_nearest_safe_places(user_lat, user_lng, limit=limit)
    return jsonify({
        "status": "success",
        "count": len(safe_places),
        "safe_places": safe_places
    })


@app.route('/api/sos-history', methods=['GET'])
def api_sos_history():
    """Returns recorded SOS alerts from MongoDB or in-memory persistence."""
    limit = request.args.get('limit', default=20, type=int)
    logs = get_sos_events(limit=limit)
    return jsonify({
        "status": "success",
        "count": len(logs),
        "events": logs
    })


@app.route('/api/voice-status', methods=['GET', 'POST'])
def api_voice_status():
    """Endpoint for testing distress voice triggers and recognition capabilities."""
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        text = data.get('text', '')
        is_distress = check_distress_phrase(text)
        return jsonify({
            "status": "success",
            "text": text,
            "distress_detected": is_distress
        })
    return jsonify({
        "status": "success",
        "voice_module_available": True,
        "supported_keywords": ["help", "bachao", "save me", "emergency", "police", "danger", "khatra", "stop"]
    })


@app.route('/send-alert', methods=['POST'])
def send_alert():
    try:
        data = request.get_json(force=True)

        alert_type = data.get('type', 'initial')
        contacts   = data.get('contacts', [])
        duration   = data.get('duration', 10)
        timestamp  = data.get('timestamp', datetime.now(timezone.utc).isoformat())
        maps_link  = data.get('maps_link', '')
        location   = data.get('location', 'Location unavailable')

        print(f"\n{'='*50}")
        print(f"[/send-alert] type={alert_type}  contacts={len(contacts)}")
        print(f"  location : {location}")
        print(f"  maps_link: {maps_link}")

        # ── Format readable timestamp ──
        try:
            ts_human = datetime.fromisoformat(
                timestamp.replace('Z', '+00:00')
            ).strftime('%d %b %Y %H:%M UTC')
        except Exception:
            ts_human = timestamp

        # ── Build message per alert type ──
        if alert_type == 'initial':
            message = (
                f"SOS ALERT — RakshaAI\n\n"
                f"Emergency signal triggered!\n"
                f"Time   : {ts_human}\n"
                f"Window : {duration} min\n"
            )
            if maps_link:
                message += f"📍 Live Location:\n{maps_link}\n"
            elif location and location != 'Location unavailable':
                message += f"📍 Coordinates: {location}\n"
            else:
                message += "📍 Location: Could not be captured\n"
            message += "\nPlease respond immediately or call 112."

        elif alert_type == 'cancel':
            message = (
                f"✅ SHE IS SAFE — RakshaAI\n\n"
                f"The SOS alert has been cancelled.\n"
                f"She is safe now. No action needed.\n"
                f"Time: {ts_human}"
            )

        elif alert_type == 'escalation':
            message = (
                f"⚠️ ESCALATION ALERT — RakshaAI\n\n"
                f"SOS was NOT cancelled in time!\n"
                f"Immediate attention required!\n"
                f"Time   : {ts_human}\n"
            )
            if maps_link:
                message += f"📍 Last Known Location:\n{maps_link}"
            elif location and location != 'Location unavailable':
                message += f"📍 Coordinates: {location}"

        else:
            message = f"RakshaAI Safety Alert — {ts_human}"

        print(f"\nMessage preview:\n{message[:120]}…\n")

        results = []

        for contact in contacts:
            name  = contact.get('name', 'Contact')
            phone = str(contact.get('phone', '')).strip()

            if not phone:
                print(f"❌ No phone number for {name}")
                results.append({"name": name, "phone": phone,
                                 "sms": "failed", "whatsapp": "failed",
                                 "batch_id": None, "sms_error": "No phone number provided"})
                continue

            print(f"\n📤 Sending to {name} ({phone})")

            # ── TextBee SMS (phone normalisation handled inside the service) ──
            tb_result  = send_textbee_sms(phone, message)
            sms_status = tb_result["status"]   # "sent" | "queued" | "failed"
            batch_id   = tb_result["batch_id"]
            sms_error  = tb_result["error"]

            # ── Twilio WhatsApp (unchanged) ──
            wa_status  = send_whatsapp_alert(phone, message)

            print(f"   SMS={sms_status} (batch={batch_id})  WA={wa_status}")

            results.append({
                "name":      name,
                "phone":     tb_result["phone"],   # normalised number
                "sms":       sms_status,
                "whatsapp":  wa_status,
                "batch_id":  batch_id,
                "sms_error": sms_error,
            })

        # ── Persist SOS alert event into database or fallback memory ──
        log_id = log_sos_event({
            "type": alert_type,
            "duration": duration,
            "timestamp": timestamp,
            "location": location,
            "maps_link": maps_link,
            "contacts_count": len(contacts),
            "results": results,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        print(f"   [SOS Log Saved] id={log_id}")

        return jsonify({"status": "success", "type": alert_type, "results": results, "log_id": log_id})

    except Exception as e:
        print(f"\n[ERROR in /send-alert] {e}")
        import traceback; traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*50)
    print("[RakshaAI] Server Starting")
    tb_key = os.getenv('TEXTBEE_API_KEY', '')
    tb_dev = os.getenv('TEXTBEE_DEVICE_ID', '')
    print(f"   TEXTBEE_API_KEY    : {'SET (' + tb_key[:8] + '...)' if tb_key else 'NOT SET'}")
    print(f"   TEXTBEE_DEVICE_ID  : {tb_dev[:12] + '...' if tb_dev else 'NOT SET'}")
    print(f"   TWILIO_WA_FROM     : {os.getenv('TWILIO_WA_FROM', 'NOT LOADED')}")
    print(f"   DATABASE           : {'MongoDB connected' if sos_collection is not None else 'Local fallback storage'}")
    # Quick connectivity check without sending any message
    tb_conn = check_textbee_connectivity()
    print(f"   TEXTBEE STATUS     : {'OK - ' + tb_conn['message'] if tb_conn['ok'] else 'WARN - ' + tb_conn['message']}")
    print("="*50 + "\n")
    app.run(debug=True, port=5000, use_reloader=False, threaded=True)
