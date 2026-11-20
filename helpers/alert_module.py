import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from the project root.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))


def get_client():
    sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    if not sid or not token or sid.startswith("ACxxx") or token.startswith("replace_with"):
        raise ValueError(
            "Twilio credentials are placeholder or missing. "
            "Please paste your real TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN into .env from https://console.twilio.com/"
        )
    return Client(sid, token)


def _normalise_phone(phone):
    phone = str(phone or "").strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if phone and not phone.startswith("+") and not phone.startswith("whatsapp:"):
        phone = "+91" + phone
    if phone.startswith("whatsapp:"):
        number = phone[len("whatsapp:"):]
        if number and not number.startswith("+"):
            number = "+91" + number
        return "whatsapp:" + number
    return phone


def send_sms_alert(to, message):
    try:
        client = get_client()
        from_num = os.getenv("TWILIO_SMS_FROM", "").strip()
        recipient = _normalise_phone(to)
        if not from_num or from_num.startswith("+1xxx"):
            print("❌ SMS failed: TWILIO_SMS_FROM is not configured with a real phone number in .env")
            return "failed"
        if not recipient or recipient.startswith("whatsapp:"):
            print("❌ SMS failed: invalid SMS recipient")
            return "failed"
        msg = client.messages.create(body=message, from_=from_num, to=recipient)
        print(f"✅ SMS accepted by Twilio. SID: {msg.sid}; status: {msg.status}")
        return "sent"
    except Exception as exc:
        err_msg = str(exc)
        print(f"❌ SMS Error: {err_msg}")
        if "Authenticate" in err_msg or "20003" in err_msg:
            print("   👉 TIP: Your TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN is incorrect in .env")
        elif "unverified" in err_msg.lower() or "21608" in err_msg:
            print(f"   👉 TIP: Recipient {to} is unverified. On Twilio Trial accounts, add it under 'Verified Caller IDs' in Twilio Console.")
        return "failed"


def send_whatsapp_alert(to, message):
    try:
        client = get_client()
        from_num = os.getenv("TWILIO_WA_FROM", "").strip()
        recipient = _normalise_phone(to)
        if not from_num:
            print("❌ WhatsApp failed: TWILIO_WA_FROM is not set in .env")
            return "failed"
        if not recipient:
            print("❌ WhatsApp failed: invalid recipient")
            return "failed"
        if not from_num.startswith("whatsapp:"):
            from_num = "whatsapp:" + from_num
        if not recipient.startswith("whatsapp:"):
            recipient = "whatsapp:" + recipient
        msg = client.messages.create(body=message, from_=from_num, to=recipient)
        print(f"✅ WhatsApp message accepted by Twilio. SID: {msg.sid}; status: {msg.status}")
        return "sent"
    except Exception as exc:
        err_msg = str(exc)
        print(f"❌ WhatsApp Error: {err_msg}")
        if "Authenticate" in err_msg or "20003" in err_msg:
            print("   👉 TIP: Your TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN is incorrect in .env")
        elif "sandbox" in err_msg.lower() or "not currently eligible" in err_msg.lower() or "63007" in err_msg or "21608" in err_msg:
            print(f"   👉 TIP: Recipient {to} must join your WhatsApp sandbox first by sending 'join <keyword>' to {from_num}")
        return "failed"
