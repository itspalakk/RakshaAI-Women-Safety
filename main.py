import os
import sys

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

# Load .env FIRST before anything else imports os.getenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Verify credentials loaded
print("=== Twilio Config Check ===")
print(f"  ACCOUNT_SID : {os.getenv('TWILIO_ACCOUNT_SID', 'NOT SET')[:8]}...")
print(f"  AUTH_TOKEN  : {'SET' if os.getenv('TWILIO_AUTH_TOKEN') else 'NOT SET'}")
print(f"  SMS_FROM    : {os.getenv('TWILIO_SMS_FROM', 'NOT SET')}")
print(f"  WA_FROM     : {os.getenv('TWILIO_WA_FROM', 'NOT SET')}")
print("===========================")

from app import app

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)