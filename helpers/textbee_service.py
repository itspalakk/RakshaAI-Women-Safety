"""
helpers/textbee_service.py
─────────────────────────────────────────────────────────────────────────────
TextBee Android-gateway SMS service for RakshaAI.

Credentials are loaded from the project-root .env file:
    TEXTBEE_API_KEY   — your TextBee API key (x-api-key header)
    TEXTBEE_DEVICE_ID — your registered Android device ID
    TEXTBEE_BASE_URL  — optional, defaults to https://api.textbee.dev/api/v1

The API endpoint used is exactly the one that was verified working in
test_textbee.py:
    POST {BASE_URL}/gateway/send-sms
    Header: x-api-key: <TEXTBEE_API_KEY>
    Body  : { "recipients": ["+91XXXXXXXXXX"],
               "message"   : "...",
               "deviceId"  : "<TEXTBEE_DEVICE_ID>" }

Returned status values understood by the frontend delivery panel:
    "sent"      — API accepted the batch and device is online
    "queued"    — API accepted but device is offline / queued
    "failed"    — API rejected or a network/config error occurred
─────────────────────────────────────────────────────────────────────────────
"""

import os
import re
import requests
from dotenv import load_dotenv

# ── Load .env from project root (safe to call multiple times) ──────────────
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))

# ── Default TextBee base URL ───────────────────────────────────────────────
_TEXTBEE_DEFAULT_BASE = "https://api.textbee.dev/api/v1"

# ── Request timeout (seconds) ─────────────────────────────────────────────
_TIMEOUT = 30


# ══════════════════════════════════════════════════════════════════════════
# Internal helpers
# ══════════════════════════════════════════════════════════════════════════

def _get_credentials():
    """
    Read TextBee credentials from environment.
    Returns (api_key, device_id, base_url) or raises ValueError if missing.
    """
    api_key   = os.getenv("TEXTBEE_API_KEY",   "").strip()
    device_id = os.getenv("TEXTBEE_DEVICE_ID", "").strip()
    base_url  = os.getenv("TEXTBEE_BASE_URL",  _TEXTBEE_DEFAULT_BASE).strip().rstrip("/")

    if not api_key:
        raise ValueError(
            "TEXTBEE_API_KEY is not set in .env. "
            "Get your API key from https://textbee.dev/dashboard"
        )
    if not device_id:
        raise ValueError(
            "TEXTBEE_DEVICE_ID is not set in .env. "
            "Find your Device ID in the TextBee dashboard after registering your Android phone."
        )
    return api_key, device_id, base_url


def _normalise_phone(raw: str) -> str:
    """
    Normalise an Indian mobile number to E.164 format (+91XXXXXXXXXX).

    Handles:
      • '9876543210'    → '+919876543210'
      • '09876543210'   → '+919876543210'  (strips leading 0)
      • '+919876543210' → '+919876543210'  (unchanged)
      • '+14155238886'  → '+14155238886'   (non-Indian, returned as-is)
    """
    phone = re.sub(r"[\s\-().+]", "", str(raw or ""))
    # Strip leading zeros for local Indian format
    if re.match(r"^0\d{9,10}$", phone):
        phone = phone.lstrip("0")
    # Prepend +91 for bare 10-digit Indian numbers
    if re.match(r"^\d{10}$", phone):
        phone = "+91" + phone
    # If still no leading +, add it
    if phone and not phone.startswith("+"):
        phone = "+" + phone
    return phone


def _is_valid_e164(phone: str) -> bool:
    """Basic E.164 validation: starts with +, then 7–15 digits."""
    return bool(re.match(r"^\+\d{7,15}$", phone))


# ══════════════════════════════════════════════════════════════════════════
# Public API
# ══════════════════════════════════════════════════════════════════════════

def send_textbee_sms(to: str, message: str) -> dict:
    """
    Send a single SMS through the TextBee Android gateway.

    Parameters
    ----------
    to      : Recipient phone number (any common format; normalised internally).
    message : Plain-text SMS body.

    Returns
    -------
    dict with keys:
        status   : "sent" | "queued" | "failed"
        phone    : Normalised recipient number used in the API call.
        batch_id : TextBee batch/message ID when available, else None.
        raw      : Full API JSON response body when available, else None.
        error    : Human-readable error string when status == "failed".
    """
    result = {
        "status":   "failed",
        "phone":    to,
        "batch_id": None,
        "raw":      None,
        "error":    None,
    }

    # ── 1. Credentials ─────────────────────────────────────────────────────
    try:
        api_key, device_id, base_url = _get_credentials()
    except ValueError as exc:
        result["error"] = str(exc)
        print(f"[TextBee] ❌ Config error: {exc}")
        return result

    # ── 2. Phone normalisation & validation ────────────────────────────────
    normalised = _normalise_phone(to)
    result["phone"] = normalised

    if not _is_valid_e164(normalised):
        result["error"] = f"Invalid phone number after normalisation: '{normalised}'"
        print(f"[TextBee] ❌ {result['error']}")
        return result

    # ── 3. Build request ───────────────────────────────────────────────────
    url     = f"{base_url}/gateway/send-sms"
    headers = {
        "x-api-key":    api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "recipients": [normalised],
        "message":    message,
        "deviceId":   device_id,
    }

    print(f"[TextBee] 📤 Sending SMS to {normalised} via device {device_id[:8]}…")

    # ── 4. HTTP call ───────────────────────────────────────────────────────
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=_TIMEOUT)
    except requests.exceptions.Timeout:
        result["error"] = (
            "TextBee request timed out after 30 s. "
            "Check that your Android device is online and the TextBee app is running."
        )
        print(f"[TextBee] ❌ Timeout: {result['error']}")
        return result
    except requests.exceptions.ConnectionError as exc:
        result["error"] = f"Network error reaching TextBee API: {exc}"
        print(f"[TextBee] ❌ Connection error: {exc}")
        return result
    except requests.exceptions.RequestException as exc:
        result["error"] = f"Unexpected HTTP error: {exc}"
        print(f"[TextBee] ❌ Request error: {exc}")
        return result

    # ── 5. Parse response ──────────────────────────────────────────────────
    try:
        body = resp.json()
    except ValueError:
        body = {"raw_text": resp.text}

    result["raw"] = body

    if resp.status_code == 429:
        result["error"] = "TextBee rate limit reached. Wait a moment before retrying."
        print(f"[TextBee] ❌ Rate limited (429)")
        return result

    if resp.status_code not in (200, 201, 202):
        # Extract meaningful error message from API body when present
        api_msg = (
            body.get("message")
            or body.get("error")
            or body.get("msg")
            or resp.text[:200]
        )
        result["error"] = f"TextBee API error {resp.status_code}: {api_msg}"
        print(f"[TextBee] ❌ API error {resp.status_code}: {api_msg}")
        return result

    # ── 6. Determine delivery status from response body ────────────────────
    # TextBee returns a batch object; check for a batchId / id field.
    batch_id = (
        body.get("data", {}).get("batchId")
        or body.get("data", {}).get("id")
        or body.get("batchId")
        or body.get("id")
    )
    result["batch_id"] = batch_id

    # Inspect the response for device-online / queued hints
    # TextBee may include "queued", "pending", "sent" in status fields
    api_status = (
        str(body.get("data", {}).get("status", ""))
        or str(body.get("status", ""))
    ).lower()

    if "queue" in api_status or "pending" in api_status:
        result["status"] = "queued"
        print(
            f"[TextBee] ⏳ SMS queued (device may be offline). "
            f"Batch: {batch_id}  status: {api_status}"
        )
    else:
        # HTTP 2xx with no explicit queued/pending → accepted for delivery
        result["status"] = "sent"
        print(
            f"[TextBee] ✅ SMS accepted. "
            f"Batch: {batch_id}  To: {normalised}"
        )

    return result


def send_textbee_sms_to_many(contacts: list, message: str) -> list:
    """
    Send the same SMS message to a list of contacts independently.
    A failure for one contact does NOT stop the others.

    Parameters
    ----------
    contacts : list of dicts with at least 'name' and 'phone' keys.
    message  : SMS body text.

    Returns
    -------
    list of dicts, one per contact:
        name     : Contact name.
        phone    : Normalised phone number.
        sms      : "sent" | "queued" | "failed"
        batch_id : TextBee batch ID or None.
        error    : Error string or None.
    """
    results = []
    for contact in contacts:
        name  = contact.get("name", "Contact")
        phone = str(contact.get("phone", "")).strip()

        print(f"\n[TextBee] ── Contact: {name} ({phone}) ──")
        outcome = send_textbee_sms(phone, message)

        results.append({
            "name":     name,
            "phone":    outcome["phone"],
            "sms":      outcome["status"],
            "batch_id": outcome["batch_id"],
            "error":    outcome["error"],
        })

    return results


def check_textbee_connectivity() -> dict:
    """
    Ping the TextBee /gateway/stats endpoint to verify API key and device.
    Safe to call at startup — does not send any SMS.

    Returns dict with:
        ok      : bool
        message : human-readable status
        data    : raw API response or None
    """
    try:
        api_key, device_id, base_url = _get_credentials()
    except ValueError as exc:
        return {"ok": False, "message": str(exc), "data": None}

    try:
        resp = requests.get(
            f"{base_url}/gateway/stats",
            headers={"x-api-key": api_key},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json() if resp.text else {}
            return {
                "ok":      True,
                "message": "TextBee API connected successfully",
                "data":    data,
            }
        return {
            "ok":      False,
            "message": f"TextBee API returned {resp.status_code}: {resp.text[:200]}",
            "data":    None,
        }
    except requests.exceptions.RequestException as exc:
        return {
            "ok":      False,
            "message": f"Cannot reach TextBee API: {exc}",
            "data":    None,
        }
