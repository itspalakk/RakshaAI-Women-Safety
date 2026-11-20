# AlertMe / RakshaAI — Setup & Documentation

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run automated test suite
python test_app.py
python test_places.py
node test_syntax.js

# 3. Start the application
python app.py
# Open http://127.0.0.1:5000 in your browser
```

---

## ✅ Twilio Diagnostic & Verification

### 1. Fill in your real `.env` credentials

Open `.env` and configure your credentials:

```ini
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx   ← 34 chars, starts with AC
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx      ← 32/35 chars
TWILIO_SMS_FROM=+1xxxxxxxxxx                            ← your Twilio phone number
TWILIO_WA_FROM=whatsapp:+14155238886                    ← Twilio WhatsApp sandbox number

# Optional: MongoDB for persistent SOS event logging
MONGODB_URI=your_mongodb_connection_string
MONGODB_DATABASE=rakshai_db
MONGODB_SOS_COLLECTION=sos_logs
```

### 2. Verify SMS & WhatsApp

```bash
python test_alert.py +91YOURMOBILENUMBER
```

### 3. WhatsApp Sandbox — one-time setup per recipient

Each recipient of WhatsApp messages on Twilio Sandbox must **first send a WhatsApp message**:
1. Open WhatsApp on the recipient's phone
2. Message `+1 415 523 8886`
3. Send text: `join <your-sandbox-keyword>`
   (Keyword located at: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)

---

## 🛠️ API Endpoints

- `GET /` — Full web application UI (Smart SOS, AI Safety Assistant, Safe Route Planner)
- `GET /ping` — Health check & Twilio SID check
- `POST /send-alert` — Triggers SMS & WhatsApp alerts to trusted contacts and persists SOS logs
- `GET /api/search-places?q=...` — Real-world autocomplete place search
- `GET /api/institutions` — Prominent colleges, hospitals & police landmarks near user
- `GET /api/nearest-safe-places?lat=...&lon=...` — Nearest verified safe havens (police stations, hospitals, staffed campuses)
- `GET /api/my-location` — Server-side IP geolocation fallback when GPS is unavailable
- `GET /api/sos-history` — Incident logs from MongoDB or local memory
- `POST /api/voice-status` — Vocal distress keyword detection

---

## 📂 File Structure

```
RakshaAI / AlertMe/
├── app.py                  ← Flask server with all connected API endpoints
├── config.py               ← MongoDB connection and SOS event logger
├── .env                    ← Environment variables and credentials
├── .env.example            ← Template environment variables
├── requirements.txt        ← Python dependencies
├── test_app.py             ← Comprehensive integration test suite
├── test_alert.py           ← Twilio diagnostic test script
├── test_places.py          ← Place search & landmark unit test
├── test_syntax.js          ← JavaScript syntax validator for index.html
├── helpers/
│   ├── alert_module.py     ← Twilio SMS and WhatsApp dispatcher
│   ├── location_module.py  ← IP-based geolocation fallback provider
│   ├── places_module.py    ← Curated landmark catalog + Nominatim & Google Places
│   └── voice_module.py     ← Distress keywords and vocal command listener
├── static/
│   └── style.css           ← Shared fallback styles
└── templates/
    └── index.html          ← Complete responsive frontend application
```
