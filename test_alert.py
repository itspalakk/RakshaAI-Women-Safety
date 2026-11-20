"""
test_alert.py — Diagnostic test for RakshaAI alert channels.

Usage:
    python test_alert.py +91XXXXXXXXXX

Replace +91XXXXXXXXXX with your own phone number.

What this tests:
  1. TextBee credentials & API connectivity.
  2. TextBee SMS delivery to the supplied number.
  3. Twilio WhatsApp delivery (requires sandbox join).
"""
import sys
import os

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

from dotenv import load_dotenv

# Load .env from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

print("\n" + "="*55)
print("  RakshaAI — Alert Channel Diagnostic Test")
print("="*55)

# ── 1. Check TextBee credentials ──────────────────────────────────────────
tb_key = os.getenv("TEXTBEE_API_KEY",   "")
tb_dev = os.getenv("TEXTBEE_DEVICE_ID", "")
tb_url = os.getenv("TEXTBEE_BASE_URL",  "https://api.textbee.dev/api/v1")
wa_f   = os.getenv("TWILIO_WA_FROM",    "")

print("\n📋 .env values loaded:")
print(f"   TEXTBEE_API_KEY    : {'✅ SET (' + tb_key[:8] + '...)' if tb_key else '❌ NOT SET'}")
print(f"   TEXTBEE_DEVICE_ID  : {'✅ SET (' + tb_dev[:8] + '...)' if tb_dev else '❌ NOT SET'}")
print(f"   TEXTBEE_BASE_URL   : {tb_url}")
print(f"   TWILIO_WA_FROM     : {wa_f or '❌ NOT SET'}")

if not tb_key or not tb_dev:
    print("\n❌ STOP: TEXTBEE_API_KEY or TEXTBEE_DEVICE_ID is missing from .env")
    print("   Get your credentials from https://textbee.dev/dashboard")
    sys.exit(1)

# ── 2. API connectivity check ─────────────────────────────────────────────
print("\n🔌 Checking TextBee API connectivity…")
from helpers.textbee_service import check_textbee_connectivity, send_textbee_sms
from helpers.alert_module import send_whatsapp_alert

conn = check_textbee_connectivity()
if conn["ok"]:
    print(f"   ✅ {conn['message']}")
else:
    print(f"   ❌ {conn['message']}")
    print("   Make sure your Android device is online and the TextBee app is running.")
    print("   Proceeding with SMS test anyway…")

# ── 3. Live send (optional) ───────────────────────────────────────────────
to_number = sys.argv[1] if len(sys.argv) > 1 else None
if not to_number:
    print("\n💡 Tip: Pass your phone number to send a real test:")
    print("   python test_alert.py +919876543210")
    print("\n   (Skipping live send — credentials check OK structurally)")
    sys.exit(0)

# ── 3a. TextBee SMS ───────────────────────────────────────────────────────
print(f"\n📤 Sending test SMS via TextBee to {to_number}…")
sms_outcome = send_textbee_sms(
    to_number,
    "✅ RakshaAI test SMS — TextBee integration is working!"
)
print(f"   SMS status : {sms_outcome['status']}")
print(f"   Batch ID   : {sms_outcome['batch_id']}")
if sms_outcome["error"]:
    print(f"   Error      : {sms_outcome['error']}")

# ── 3b. Twilio WhatsApp ───────────────────────────────────────────────────
print(f"\n📲 Sending test WhatsApp to {to_number}…")
print("   ⚠️  Sandbox: recipient must first send 'join <keyword>'")
print("       to whatsapp:+14155238886")
wa_result = send_whatsapp_alert(
    to_number,
    "✅ RakshaAI test WhatsApp — if you received this, WA is working!"
)
print(f"   WhatsApp result: {wa_result}")

# ── 4. Summary ────────────────────────────────────────────────────────────
print("\n" + "="*55)
if sms_outcome["status"] in ("sent", "queued"):
    if sms_outcome["status"] == "queued":
        print("⏳ SMS queued — device may be offline. Check TextBee app.")
    else:
        print("✅ SMS accepted by TextBee successfully!")
else:
    print("❌ SMS failed. Check the error above.")
    print("   Common causes: device offline, TextBee app not running,")
    print("   wrong API key / device ID, or no SIM credit.")

if wa_result == "sent":
    print("✅ WhatsApp is working correctly!")
else:
    print("⚠️  WhatsApp failed. Did the recipient join the sandbox first?")
    print("   → Have them send 'join <keyword>' to +14155238886 on WhatsApp")
print("="*55 + "\n")